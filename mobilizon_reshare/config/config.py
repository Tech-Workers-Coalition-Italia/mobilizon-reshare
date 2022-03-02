import importlib.resources
import logging
from pathlib import Path
from typing import Optional

import pkg_resources
from appdirs import AppDirs
from dynaconf import Dynaconf, Validator

import mobilizon_reshare
from mobilizon_reshare.config import strategies, publishers, notifiers
from mobilizon_reshare.config.notifiers import notifier_names
from mobilizon_reshare.config.publishers import publisher_names

logger = logging.getLogger(__name__)

base_validators = [
    # strategy to decide events to publish
    Validator("selection.strategy", must_exist=True, is_type_of=str),
    # url of the main Mobilizon instance to download events from
    Validator("source.mobilizon.url", must_exist=True, is_type_of=str),
    Validator("source.mobilizon.group", must_exist=True, is_type_of=str),
]

activeness_validators = [
    Validator(f"publisher.{publisher_name}.active", must_exist=True, is_type_of=bool)
    for publisher_name in publisher_names
] + [
    Validator(f"notifier.{notifier_name}.active", must_exist=True, is_type_of=bool)
    for notifier_name in notifier_names
]


def current_version() -> str:
    with importlib.resources.open_text(mobilizon_reshare, "VERSION") as fp:
        return fp.read()


def get_settings_files_paths() -> Optional[str]:

    dirs = AppDirs(appname="mobilizon-reshare", version=current_version())
    bundled_settings_path = pkg_resources.resource_filename(
        "mobilizon_reshare", "settings.toml"
    )
    for config_path in [
        Path(dirs.user_config_dir, "mobilizon_reshare.toml").absolute(),
        Path(dirs.site_config_dir, "mobilizon_reshare.toml").absolute(),
        bundled_settings_path,
    ]:
        if config_path and Path(config_path).exists():
            logger.debug(f"Loading configuration from {config_path}")
            return config_path


def build_settings(validators: Optional[list[Validator]] = None):
    """
    Creates a Dynaconf base object. Configuration files are checked in this order:

      1. User configuration directory. On Linux that's `$XDG_CONFIG_HOME/mobilizon_reshare/<mobilizon-reshare-version>`;
      2. System configuration directory. On Linux that's the first element of
         `$XDG_CONFIG_DIRS` + `/mobilizon_reshare/<mobilizon-reshare-version>`.
      3. The default configuration distributed with the package.

    The first available configuration file will be loaded.
    """
    ENVVAR_PREFIX = "MOBILIZON_RESHARE"
    config = Dynaconf(
        environments=True,
        envvar_prefix=ENVVAR_PREFIX,
        settings_files=get_settings_files_paths(),
        validators=validators or [],
    )

    # TODO use validation control in dynaconf 3.2.0 once released
    config.validators.validate()
    return config


def build_and_validate_settings():
    """
    Creates a settings object to be used in the application. It collects and apply generic validators and validators
    specific for each publisher, notifier and publication strategy.
    """

    # we first do a preliminary load of the settings without validation. We will later use them to determine which
    # publishers, notifiers and strategy have been selected
    raw_settings = build_settings(validators=activeness_validators)

    # we retrieve validators that are conditional. Each module will analyze the settings and decide which validators
    # need to be applied.
    strategy_validators = strategies.get_validators(raw_settings)
    publisher_validators = publishers.get_validators(raw_settings)
    notifier_validators = notifiers.get_validators(raw_settings)

    # we rebuild the settings, providing all the selected validators.
    settings = build_settings(
        base_validators
        + strategy_validators
        + publisher_validators
        + notifier_validators,
    )

    return settings


# this singleton and functions are necessary to put together
# the necessities of the testing suite, the CLI and still having a single entrypoint to the config.
# The CLI needs to provide the settings file at run time so we cannot work at import time.
# The normal Dynaconf options to specify the settings files are also not a valid option because of the two steps
# validation that prevents us to employ their mechanism to specify settings files. This could probably be reworked
# better in the future.


class CustomConfig:
    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.settings = build_and_validate_settings()

    @classmethod
    def clear(cls):
        cls._instance = None


def get_settings():
    return CustomConfig.get_instance().settings
