from dynaconf import Validator


telegram_validators = [
    Validator("publisher.telegram.chat_id", must_exist=True),
    Validator("publisher.telegram.msg_template_path", must_exist=True, default=None),
    Validator("publisher.telegram.recap_template_path", must_exist=True, default=None),
    Validator(
        "publisher.telegram.recap_header_template_path", must_exist=True, default=None
    ),
    Validator("publisher.telegram.token", must_exist=True),
    Validator("publisher.telegram.username", must_exist=True),
]
zulip_validators = [
    Validator("publisher.zulip.instance", must_exist=True),
    Validator("publisher.zulip.chat_id", must_exist=True),
    Validator("publisher.zulip.subject", must_exist=True),
    Validator("publisher.zulip.msg_template_path", must_exist=True, default=None),
    Validator("publisher.zulip.recap_template_path", must_exist=True, default=None),
    Validator(
        "publisher.zulip.recap_header_template_path", must_exist=True, default=None
    ),
    Validator("publisher.zulip.bot_token", must_exist=True),
    Validator("publisher.zulip.bot_email", must_exist=True),
]
mastodon_validators = [
    Validator("publisher.mastodon.instance", must_exist=True),
    Validator("publisher.mastodon.token", must_exist=True),
    Validator("publisher.mastodon.toot_length", default=500),
    Validator("publisher.mastodon.msg_template_path", must_exist=True, default=None),
    Validator("publisher.mastodon.recap_template_path", must_exist=True, default=None),
    Validator(
        "publisher.mastodon.recap_header_template_path", must_exist=True, default=None
    ),
    Validator("publisher.mastodon.name", must_exist=True),
]
twitter_validators = [
    Validator("publisher.twitter.msg_template_path", must_exist=True, default=None),
    Validator("publisher.twitter.recap_template_path", must_exist=True, default=None),
    Validator(
        "publisher.twitter.recap_header_template_path", must_exist=True, default=None
    ),
    Validator("publisher.twitter.api_key", must_exist=True),
    Validator("publisher.twitter.api_key_secret", must_exist=True),
    Validator("publisher.twitter.access_token", must_exist=True),
    Validator("publisher.twitter.access_secret", must_exist=True),
]
facebook_validators = [
    Validator("publisher.facebook.msg_template_path", must_exist=True, default=None),
    Validator("publisher.facebook.recap_template_path", must_exist=True, default=None),
    Validator(
        "publisher.facebook.recap_header_template_path", must_exist=True, default=None
    ),
    Validator("publisher.facebook.page_access_token", must_exist=True),
]

publisher_name_to_validators = {
    "telegram": telegram_validators,
    "facebook": facebook_validators,
    "twitter": twitter_validators,
    "mastodon": mastodon_validators,
    "zulip": zulip_validators,
}
publisher_names = publisher_name_to_validators.keys()


def get_active_publishers(settings):
    return list(
        filter(
            lambda publisher_name: settings["publisher"][publisher_name]["active"],
            publisher_names,
        )
    )


def get_validators(settings):
    active_publishers = get_active_publishers(settings)
    validators = []
    for publisher in active_publishers:
        validators += publisher_name_to_validators[publisher]
    return validators
