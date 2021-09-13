from typing import Iterator

from dynaconf import Validator

telegram_validators = [
    Validator("notifier.telegram.chat_id", must_exist=True),
    Validator("notifier.telegram.token", must_exist=True),
    Validator("notifier.telegram.username", must_exist=True),
]
zulip_validators = [
    Validator("publisher.zulip.chat_id", must_exist=True),
    Validator("publisher.zulip.subject", must_exist=True),
    Validator("publisher.zulip.msg_template_path", must_exist=True, default=None),
    Validator("publisher.zulip.bot_token", must_exist=True),
    Validator("publisher.zulip.bot_email", must_exist=True),
]
mastodon_validators = []
twitter_validators = []

notifier_name_to_validators = {
    "telegram": telegram_validators,
    "twitter": twitter_validators,
    "mastodon": mastodon_validators,
    "zulip": zulip_validators,
}
notifier_names = notifier_name_to_validators.keys()


def get_active_notifiers(settings) -> Iterator[str]:
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
