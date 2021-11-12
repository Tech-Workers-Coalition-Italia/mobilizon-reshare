from mobilizon_reshare.publishers.platforms.facebook import (
    FacebookPublisher,
    FacebookFormatter,
    FacebookNotifier,
)
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

"""
This module is required to have an explicit mapping between platform names and the classes implementing those platforms.
It could be refactored in a different pattern but this way makes it more explicit and linear. Eventually this could be
turned into a plugin system with a plugin for each platform."""

name_to_publisher_class = {
    "mastodon": MastodonPublisher,
    "telegram": TelegramPublisher,
    "zulip": ZulipPublisher,
    "twitter": TwitterPublisher,
    "facebook": FacebookPublisher,
}
name_to_formatter_class = {
    "mastodon": MastodonFormatter,
    "telegram": TelegramFormatter,
    "zulip": ZulipFormatter,
    "twitter": TwitterFormatter,
    "facebook": FacebookFormatter,
}
name_to_notifier_class = {
    "mastodon": MastodonNotifier,
    "telegram": TelegramNotifier,
    "zulip": ZulipNotifier,
    "twitter": TwitterNotifier,
    "facebook": FacebookNotifier,
}


def get_notifier_class(platform):
    return name_to_notifier_class[platform]


def get_publisher_class(platform):
    return name_to_publisher_class[platform]


def get_formatter_class(platform):
    return name_to_formatter_class[platform]
