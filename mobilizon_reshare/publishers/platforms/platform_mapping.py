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
    "telegram": TelegramPublisher,
    "zulip": ZulipPublisher,
    "twitter": TwitterPublisher,
}
name_to_formatter_class = {
    "telegram": TelegramFormatter,
    "zulip": ZulipFormatter,
    "twitter": TwitterFormatter,
}
name_to_notifier_class = {
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
