from dataclasses import dataclass, field

from mobilizon_bots.config.config import settings
from mobilizon_bots.config.publishers import get_active_publishers
from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus
from .exceptions import PublisherError
from .abstract import AbstractPublisher
from .telegram import TelegramPublisher

KEY2CLS = {"telegram": TelegramPublisher}


@dataclass
class PublisherReport:
    status: PublicationStatus
    reason: str
    publisher: AbstractPublisher
    event: MobilizonEvent


@dataclass
class PublisherCoordinatorReport:
    reports: list = field(default_factory=[])

    @property
    def successful(self):
        return all(r.status == PublicationStatus.COMPLETED for r in self.reports)


class PublisherCoordinator:
    def __init__(self, event: MobilizonEvent):
        self.publishers = tuple(
            KEY2CLS[pn](event) for pn in get_active_publishers(settings)
        )

    def run(self) -> PublisherCoordinatorReport:
        invalid_credentials, invalid_event, invalid_msg = self._validate()
        if invalid_credentials or invalid_event or invalid_msg:
            return PublisherCoordinatorReport(
                reports=invalid_credentials + invalid_event + invalid_msg
            )

        failed_publishers = self._post()
        if failed_publishers:
            return PublisherCoordinatorReport(reports=failed_publishers)

        return PublisherCoordinatorReport(
            reports=[
                PublisherReport(
                    status=PublicationStatus.COMPLETED,
                    reason="",
                    publisher=p,
                    event=p.event,
                )
                for p in self.publishers
            ],
        )

    def _post(self):
        failed_publishers = []
        for p in self.publishers:
            try:
                p.post()
            except PublisherError as e:
                failed_publishers.append(
                    PublisherReport(
                        status=PublicationStatus.FAILED,
                        reason=repr(e),
                        publisher=p,
                        event=p.event,
                    )
                )
        return failed_publishers

    def _validate(self):
        invalid_credentials, invalid_event, invalid_msg = [], [], []
        for p in self.publishers:
            if not p.are_credentials_valid():
                invalid_credentials.append(
                    PublisherReport(
                        status=PublicationStatus.FAILED,
                        reason="Invalid credentials",
                        publisher=p,
                        event=p.event,
                    )
                )
            if not p.is_event_valid():
                invalid_event.append(
                    PublisherReport(
                        status=PublicationStatus.FAILED,
                        reason="Invalid event",
                        publisher=p,
                        event=p.event,
                    )
                )
            if not p.is_message_valid():
                invalid_msg.append(
                    PublisherReport(
                        status=PublicationStatus.FAILED,
                        reason="Invalid message",
                        publisher=p,
                        event=p.event,
                    )
                )
        return invalid_credentials, invalid_event, invalid_msg
