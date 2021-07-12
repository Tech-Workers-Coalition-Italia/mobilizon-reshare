from dataclasses import dataclass, field
from typing import List

from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus
from mobilizon_bots.publishers import get_active_publishers
from mobilizon_bots.publishers.abstract import AbstractPublisher
from mobilizon_bots.publishers.exceptions import PublisherError
from mobilizon_bots.publishers.telegram import TelegramPublisher

KEY2CLS = {"telegram": TelegramPublisher}


@dataclass
class PublisherReport:
    status: PublicationStatus
    reason: str
    publisher: AbstractPublisher


@dataclass
class PublisherCoordinatorReport:
    reports: List[PublisherReport] = field(default_factory=[])

    @property
    def successful(self):
        return all(r.status == PublicationStatus.COMPLETED for r in self.reports)

    def __iter__(self):
        return self.reports.__iter__()


class PublisherCoordinator:
    def __init__(self, event: MobilizonEvent):
        self.publishers = tuple(KEY2CLS[pn](event) for pn in get_active_publishers())

    def run(self) -> PublisherCoordinatorReport:
        invalid_credentials, invalid_event, invalid_msg = self._validate()
        errors = invalid_credentials + invalid_event + invalid_msg
        if errors:
            return PublisherCoordinatorReport(reports=errors)

        return self._post()

    def _make_successful_report(self):
        return [
            PublisherReport(status=PublicationStatus.COMPLETED, reason="", publisher=p,)
            for p in self.publishers
        ]

    def _post(self):
        failed_publishers_reports = []
        for p in self.publishers:
            try:
                p.post()
            except PublisherError as e:
                failed_publishers_reports.append(
                    PublisherReport(
                        status=PublicationStatus.FAILED, reason=repr(e), publisher=p,
                    )
                )
        reports = failed_publishers_reports or self._make_successful_report()
        return PublisherCoordinatorReport(reports)

    def _validate(self):
        invalid_credentials, invalid_event, invalid_msg = [], [], []
        for p in self.publishers:
            if not p.are_credentials_valid():
                invalid_credentials.append(
                    PublisherReport(
                        status=PublicationStatus.FAILED,
                        reason="Invalid credentials",
                        publisher=p,
                    )
                )
            if not p.is_event_valid():
                invalid_event.append(
                    PublisherReport(
                        status=PublicationStatus.FAILED,
                        reason="Invalid event",
                        publisher=p,
                    )
                )
            if not p.is_message_valid():
                invalid_msg.append(
                    PublisherReport(
                        status=PublicationStatus.FAILED,
                        reason="Invalid message",
                        publisher=p,
                    )
                )
        return invalid_credentials, invalid_event, invalid_msg
