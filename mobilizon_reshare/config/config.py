import importlib.resources
import os
from pathlib import Path
from typing import Optional

from appdirs import AppDirs
from dynaconf import Dynaconf, Validator

import mobilizon_reshare
from mobilizon_reshare.config import strategies, publishers, notifiers
from mobilizon_reshare.config.notifiers import notifier_names

from mobilizon_reshare.config.publishers import publisher_names

base_validators = [
    # strategy to decide events to publish
    Validator("selection.strategy", must_exist=True, is_type_of=str),
    Validator(
        "publishing.window.begin",
        must_exist=True,
        is_type_of=int,
        gte=0,
        lte=24,
    ),
    Validator("publishing.window.end", must_exist=True, is_type_of=int, gte=0, lte=24),
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


def build_settings(
    settings_file: Optional[str] = None, validators: Optional[list[Validator]] = None
):
    """
    Creates a Dynaconf base object. Configuration files are checked in this order:

      1. CLI argument
      2. `MOBILIZION_RESHARE_SETTINGS_FILE` environment variable;
      3. User configuration directory. On Linux that's `$XDG_CONFIG_HOME/mobilizon_reshare/<mobilizon-reshare-version>`;
      4. User configuration directory. On Linux that's the first element of
         `$XDG_CONFIG_DIRS` + `/mobilizon_reshare/<mobilizon-reshare-version>`.
      5. The default configuration distributed with the package.

    The first available configuration file will be loaded.
    """
    dirs = AppDirs(appname="mobilizon-reshare", version=current_version())
    with importlib.resources.path(
        mobilizon_reshare, "settings.toml"
    ) as bundled_settings_path:
        SETTINGS_FILE = [
            bundled_settings_path,
            Path(dirs.site_config_dir, "mobilizon_reshare.toml"),
            Path(dirs.user_config_dir, "mobilizon_reshare.toml"),
            os.environ.get("MOBILIZION_RESHARE_SETTINGS_FILE"),
            settings_file,
        ]

    ENVVAR_PREFIX = "MOBILIZON_RESHARE"
    return Dynaconf(
        environments=True,
        envvar_prefix=ENVVAR_PREFIX,
        settings_files=SETTINGS_FILE,
        validators=validators or [],
    )


def build_and_validate_settings(settings_file: Optional[str] = None):
    """
    Creates a settings object to be used in the application. It collects and apply generic validators and validators
    specific for each publisher, notifier and publication strategy.
    """

    # we first do a preliminary load of the settings without validation. We will later use them to determine which
    # publishers, notifiers and strategy have been selected
    raw_settings = build_settings(
        settings_file=settings_file, validators=activeness_validators
    )

    # we retrieve validators that are conditional. Each module will analyze the settings and decide which validators
    # need to be applied.
    strategy_validators = strategies.get_validators(raw_settings)
    publisher_validators = publishers.get_validators(raw_settings)
    notifier_validators = notifiers.get_validators(raw_settings)

    # we rebuild the settings, providing all the selected validators.
    settings = build_settings(
        settings_file,
        base_validators
        + strategy_validators
        + publisher_validators
        + notifier_validators,
    )
    # TODO use validation control in dynaconf 3.2.0 once released
    settings.validators.validate()
    return settings


# this singleton and functions are necessary to put together
# the necessities of the testing suite, the CLI and still having a single entrypoint to the config.
# The CLI needs to provide the settings file at run time so we cannot work at import time.
# The normal Dynaconf options to specify the settings files are also not a valid option because of the two steps
# validation that prevents us to employ their mechanism to specify settings files. This could probably be reworked
# better in the future.
class CustomConfig:
    _instance = None
    _settings_file = None

    def __new__(cls, settings_file: Optional[str] = None):
        if (
            settings_file is None and cls._settings_file is not None
        ):  # normal access, I don't want to reload
            return cls._instance

        if (
            cls._instance is None and cls._settings_file is None
        ) or settings_file != cls._settings_file:
            cls._settings_file = settings_file
            cls._instance = super(CustomConfig, cls).__new__(cls)
            cls.settings = build_and_validate_settings(settings_file)

        return cls._instance

    def update(self, settings_file: Optional[str] = None):
        self.settings = build_and_validate_settings(settings_file)


def get_settings(settings_file: Optional[str] = None):
    config = CustomConfig(settings_file)
    return config.settings
