from dataclasses import dataclass, field

from mobilizon_bots.config.config import settings
from mobilizon_bots.config.publishers import get_active_publishers
from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus
from .exceptions import PublisherError
from .telegram import TelegramPublisher

KEY2CLS = {"telegram": TelegramPublisher}


@dataclass
class PublisherCoordinatorResult:
    status: PublicationStatus
    description: str
    invalid_credentials_publishers: list = field(default_factory=[])
    invalid_event_publishers: list = field(default_factory=[])
    invalid_msg_publishers: list = field(default_factory=[])
    failed_publishers: list = field(default_factory=[])
    successful_publishers: list = field(default_factory=[])


class PublisherCoordinator:
    def __init__(self, event: MobilizonEvent):
        self.publishers = tuple(
            KEY2CLS[pn](event) for pn in get_active_publishers(settings)
        )

    def run(self) -> PublisherCoordinatorResult:
        invalid_credentials, invalid_event, invalid_msg = self._validate()
        if invalid_credentials or invalid_event or invalid_msg:
            return PublisherCoordinatorResult(
                status=PublicationStatus.FAILED,
                description="Validation failed for at least 1 publisher",
                invalid_credentials_publishers=invalid_credentials,
                invalid_event_publishers=invalid_event,
                invalid_msg_publishers=invalid_msg,
            )

        failed_publishers, successful_publishers = self._post()
        if failed_publishers:
            return PublisherCoordinatorResult(
                status=PublicationStatus.FAILED,
                description="Posting failed for at least 1 publisher",
                failed_publishers=failed_publishers,
                successful_publishers=successful_publishers,
            )

        return PublisherCoordinatorResult(
            status=PublicationStatus.COMPLETED,
            description="https://www.youtube.com/watch?v=2lHgmC6PBBE",
        )

    def _post(self):
        failed_publishers, successful_publishers = [], []
        for p in self.publishers:
            try:
                p.post()
            except PublisherError:
                failed_publishers.append(p)
            else:
                successful_publishers.append(p)
        return failed_publishers, successful_publishers

    def _validate(self):
        invalid_credentials, invalid_event, invalid_msg = [], [], []
        for p in self.publishers:
            if not p.are_credentials_valid():
                invalid_credentials.append(p)
            if not p.is_event_valid():
                invalid_event.append(p)
            if not p.is_message_valid():
                invalid_msg.append(p)
        return invalid_credentials, invalid_event, invalid_msg
