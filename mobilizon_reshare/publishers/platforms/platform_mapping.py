from mobilizon_reshare.publishers.platforms.telegram import (
    TelegramPublisher,
    TelegramFormatter,
    TelegramNotifier,
)
from mobilizon_reshare.publishers.platforms.zulip import (
    ZulipPublisher,
    ZulipFormatter,
    ZulipNotifier,
)

name_to_publisher_class = {
    "telegram": TelegramPublisher,
    "zulip": ZulipPublisher,
}
name_to_formatter_class = {
    "telegram": TelegramFormatter,
    "zulip": ZulipFormatter,
}
name_to_notifier_class = {
    "telegram": TelegramNotifier,
    "zulip": ZulipNotifier,
}


def get_notifier_class(platform):
    return name_to_notifier_class[platform]


def get_publisher_class(platform):
    return name_to_publisher_class[platform]


def get_formatter_class(platform):
    return name_to_formatter_class[platform]
