from dynaconf import Validator

telegram_validators = [Validator("notifier.telegram.chat_id", must_exist=True)]
zulip_validators = []
mastodon_validators = []
twitter_validators = []

notifier_name_to_validators = {
    "telegram": telegram_validators,
    "twitter": twitter_validators,
    "mastodon": mastodon_validators,
    "zulip": zulip_validators,
}
notifier_names = notifier_name_to_validators.keys()


def get_active_notifiers(settings):
    return filter(
        lambda notifier_name: settings["notifier"][notifier_name]["active"],
        notifier_names,
    )


def get_validators(settings):
    active_notifiers = get_active_notifiers(settings)
    validators = []
    for notifier in active_notifiers:
        validators += notifier_name_to_validators[notifier]
    return validators
