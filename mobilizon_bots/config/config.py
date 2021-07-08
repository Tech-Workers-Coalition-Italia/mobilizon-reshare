import os
from typing import List

from dynaconf import Dynaconf, Validator

from mobilizon_bots.config import strategies, publishers, notifiers
from mobilizon_bots.config.notifiers import notifier_names
from mobilizon_bots.config.publishers import publisher_names


def build_settings(
    settings_files: List[str] = None, validators: List[Validator] = None
):

    SETTINGS_FILE = (
        settings_files
        or os.environ.get("MOBILIZON_BOTS_SETTINGS_FILE")
        or [
            "mobilizon_bots/settings.toml",
            "mobilizon_bots/.secrets.toml",
            "/etc/mobilizon_bots.toml",
            "/etc/mobilizon_bots_secrets.toml",
        ]
    )
    ENVVAR_PREFIX = "MOBILIZON_BOTS"

    return Dynaconf(
        environments=True,
        envvar_prefix=ENVVAR_PREFIX,
        settings_files=SETTINGS_FILE,
        validators=validators or [],
    )


def build_and_validate_settings(settings_files: List[str] = None):
    """
    Creates a settings object to be used in the application. It collects and apply generic validators and validators
    specific for each publisher, notifier and publication strategy.
    """

    # we first do a preliminary load of the settings without validation. We will later use them to determine which
    # publishers, notifiers and strategy have been selected
    raw_settings = build_settings(settings_files=settings_files)

    # These validators are always applied
    base_validators = (
        [
            # strategy to decide events to publish
            Validator("selection.strategy", must_exist=True, is_type_of=str),
            Validator(
                "publishing.window.begin",
                must_exist=True,
                is_type_of=int,
                gte=0,
                lte=24,
            ),
            Validator(
                "publishing.window.end", must_exist=True, is_type_of=int, gte=0, lte=24
            ),
            # url of the main Mobilizon instance to download events from
            Validator("source.mobilizon.url", must_exist=True, is_type_of=str),
            Validator("source.mobilizon.group", must_exist=True, is_type_of=str),
        ]
        + [
            Validator(
                f"publisher.{publisher_name}.active", must_exist=True, is_type_of=bool
            )
            for publisher_name in publisher_names
        ]
        + [
            Validator(
                f"notifier.{notifier_name}.active", must_exist=True, is_type_of=bool
            )
            for notifier_name in notifier_names
        ]
    )

    # we retrieve validators that are conditional. Each module will analyze the settings and decide which validators
    # need to be applied.
    strategy_validators = strategies.get_validators(raw_settings)
    publisher_validators = publishers.get_validators(raw_settings)
    notifier_validators = notifiers.get_validators(raw_settings)

    # we rebuild the settings, providing all the selected validators.
    settings = build_settings(
        settings_files,
        base_validators
        + strategy_validators
        + publisher_validators
        + notifier_validators,
    )
    # TODO use validation control in dynaconf 3.2.0 once released
    settings.validators.validate()
    return settings


class CustomConfig:
    _instance = None

    def __new__(cls, settings_files: List[str] = None):
        if cls._instance is None:
            print("Creating the object")
            cls._instance = super(CustomConfig, cls).__new__(cls)
            cls.settings = build_settings(settings_files)
        return cls._instance

    def update(self, settings_files: List[str] = None):
        self.settings = build_settings(settings_files)


def get_settings(settings_files: List[str] = None):
    config = CustomConfig(settings_files)
    return config.settings


def update_settings_files(settings_files: List[str] = None):
    CustomConfig().update(settings_files)
    return CustomConfig().settings
