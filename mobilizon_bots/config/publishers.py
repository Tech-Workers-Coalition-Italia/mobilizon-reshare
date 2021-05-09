from dynaconf import Validator

telegram_validators = [Validator("publisher.telegram.chat_id", must_exist=True)]
zulip_validators = []
mastodon_validators = []
twitter_validators = []
facebook_validators = []

publisher_name_to_validators = {
    "telegram": telegram_validators,
    "facebook": facebook_validators,
    "twitter": twitter_validators,
    "mastodon": mastodon_validators,
    "zulip": zulip_validators,
}
publisher_names = publisher_name_to_validators.keys()


def get_active_publishers(settings):
    return filter(
        lambda publisher_name: settings["publisher"][publisher_name]["active"],
        publisher_names,
    )


def get_validators(settings):
    active_publishers = get_active_publishers(settings)
    validators = []
    for publisher in active_publishers:
        validators += publisher_name_to_validators[publisher]
    return validators
