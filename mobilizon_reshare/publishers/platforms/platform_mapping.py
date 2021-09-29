from mobilizon_reshare.publishers.platforms.telegram import (
    TelegramPublisher,
    TelegramFormatter,
)
from mobilizon_reshare.publishers.platforms.zulip import (
    ZulipPublisher,
    ZulipFormatter,
)

name_to_publisher_class = {
    "telegram": TelegramPublisher,
    "zulip": ZulipPublisher,
}
name_to_formatter_class = {
    "telegram": TelegramFormatter,
    "zulip": ZulipFormatter,
}


def get_publisher_class(platform):
    return name_to_publisher_class[platform]


def get_formatter_class(platform):
    return name_to_formatter_class[platform]
