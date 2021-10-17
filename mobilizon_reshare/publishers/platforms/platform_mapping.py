from mobilizon_reshare.publishers.platforms.mastodon import (
    MastodonPublisher,
    MastodonFormatter,
    MastodonNotifier,
)
from mobilizon_reshare.publishers.platforms.telegram import (
    TelegramPublisher,
    TelegramFormatter,
    TelegramNotifier,
)
from mobilizon_reshare.publishers.platforms.twitter import (
    TwitterPublisher,
    TwitterFormatter,
    TwitterNotifier,
)
from mobilizon_reshare.publishers.platforms.zulip import (
    ZulipPublisher,
    ZulipFormatter,
    ZulipNotifier,
)

name_to_publisher_class = {
    "mastodon": MastodonPublisher,
    "telegram": TelegramPublisher,
    "zulip": ZulipPublisher,
    "twitter": TwitterPublisher,
}
name_to_formatter_class = {
    "mastodon": MastodonFormatter,
    "telegram": TelegramFormatter,
    "zulip": ZulipFormatter,
    "twitter": TwitterFormatter,
}
name_to_notifier_class = {
    "mastodon": MastodonNotifier,
    "telegram": TelegramNotifier,
    "zulip": ZulipNotifier,
    "twitter": TwitterNotifier,
}


def get_notifier_class(platform):
    return name_to_notifier_class[platform]


def get_publisher_class(platform):
    return name_to_publisher_class[platform]


def get_formatter_class(platform):
    return name_to_formatter_class[platform]
