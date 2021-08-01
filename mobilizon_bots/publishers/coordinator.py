from dataclasses import dataclass, field
from uuid import UUID

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.models.publication import PublicationStatus
from mobilizon_bots.publishers.exceptions import PublisherError
from mobilizon_bots.publishers.telegram import TelegramPublisher

KEY2CLS = {"telegram": TelegramPublisher}


@dataclass
class PublicationReport:
    status: PublicationStatus
    reason: str


@dataclass
class PublisherCoordinatorReport:
    reports: dict[UUID, PublicationReport] = field(default_factory={})

    @property
    def successful(self):
        return all(
            r.status == PublicationStatus.COMPLETED for r in self.reports.values()
        )

    def __iter__(self):
        return self.reports.items().__iter__()


class PublisherCoordinator:
    def __init__(self, event: MobilizonEvent, publications: list[tuple[UUID, str]]):
        self.publications = tuple(
            (uuid, KEY2CLS[pn](event)) for uuid, pn in publications
        )

    def run(self) -> PublisherCoordinatorReport:
        errors = self._validate()
        if errors:
            return PublisherCoordinatorReport(reports=errors)

        return self._post()

    def _make_successful_report(self):
        return {
            uuid: PublicationReport(
                status=PublicationStatus.COMPLETED,
                reason="",
            )
            for uuid, _ in self.publications
        }

    def _post(self):
        failed_publishers_reports = {}
        for uuid, p in self.publications:
            try:
                p.post()
            except PublisherError as e:
                failed_publishers_reports[uuid] = PublicationReport(
                    status=PublicationStatus.FAILED,
                    reason=repr(e),
                )
        reports = failed_publishers_reports or self._make_successful_report()
        return PublisherCoordinatorReport(reports)

    def _validate(self):
        errors: dict[UUID, PublicationReport] = {}
        for uuid, p in self.publications:
            reason = []
            if not p.are_credentials_valid():
                reason.append("Invalid credentials")
            if not p.is_event_valid():
                reason.append("Invalid event")
            if not p.is_message_valid():
                reason.append("Invalid message")

            if len(reason) > 0:
                errors[uuid] = PublicationReport(
                    status=PublicationStatus.FAILED, reason=", ".join(reason)
                )

        return errors
