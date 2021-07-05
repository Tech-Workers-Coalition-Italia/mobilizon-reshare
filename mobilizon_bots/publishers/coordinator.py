from mobilizon_bots.config.config import settings
from mobilizon_bots.config.publishers import get_active_publishers
from mobilizon_bots.event.event import MobilizonEvent
from .exceptions import PublisherError
from .telegram import TelegramPublisher

KEY2CLS = {"telegram": TelegramPublisher}


class PublisherCoordinator:
    def __init__(self, event: MobilizonEvent):
        self.publishers = tuple(
            KEY2CLS[pn](event) for pn in get_active_publishers(settings)
        )

    def run(self) -> dict:
        invalid_credentials, invalid_event, invalid_msg = [], [], []
        for p in self.publishers:
            if not p.are_credentials_valid():
                invalid_credentials.append(p)
            if not p.is_event_valid():
                invalid_event.append(p)
            if not p.is_message_valid():
                invalid_msg.append(p)
        if invalid_credentials or invalid_event or invalid_msg:
            # TODO: consider to use exceptions or data class if necessary
            return {
                "status": "fail",
                "description": "Validation failed for at least 1 publisher",
                "invalid_credentials": invalid_credentials,
                "invalid_event": invalid_event,
                "invalid_msg": invalid_msg,
            }

        failed_publishers, successful_publishers = [], []
        for p in self.publishers:
            try:
                p.post()
            except PublisherError:
                failed_publishers.append(p)
            else:
                successful_publishers.append(p)

        if failed_publishers:
            return {
                "status": "fail",
                "description": "Posting failed for at least 1 publisher",
                "failed_publishers": failed_publishers,
                "successful_publishers": successful_publishers,
            }
        return {
            "status": "success",
            "description": "https://www.youtube.com/watch?v=2lHgmC6PBBE",
        }
