from mobilizon_reshare.publishers.platforms.telegram import (
    TelegramPublisher,
    TelegramFormatter,
)
from mobilizon_reshare.publishers.platforms.zulip import ZulipPublisher

name_to_publisher_class = {"telegram": TelegramPublisher, "zulip": ZulipPublisher}
name_to_formatter_class = {"telegram": TelegramFormatter, "zulip": None}
