from dynaconf import Dynaconf, Validator

from mobilizon_bots.config import strategies, publishers
from mobilizon_bots.config.publishers import publisher_names

SETTINGS_FILE = [
    "mobilizon_bots/settings.toml",
    "mobilizon_bots/.secrets.toml",
    "/etc/mobilizon_bots.toml",
    "/etc/mobilizon_bots_secrets.toml",
]
ENVVAR_PREFIX = "MOBILIZON_BOTS"
base_validators = [Validator("selection.strategy", must_exist=True)] + [
    Validator(f"publisher.{publisher_name}.active", must_exist=True, is_type_of=bool)
    for publisher_name in publisher_names
]

raw_settings = Dynaconf(
    environments=True,
    envvar_prefix=ENVVAR_PREFIX,
    settings_files=SETTINGS_FILE,
    validators=base_validators,
)

strategy_validators = strategies.get_validators(raw_settings)
publisher_validators = publishers.get_validators(raw_settings)

settings = Dynaconf(
    environments=True,
    envvar_prefix=ENVVAR_PREFIX,
    settings_files=SETTINGS_FILE,
    validators=base_validators + strategy_validators + publisher_validators,
)
# TODO use validation control in dynaconf 3.2.0 once released
settings.validators.validate()
