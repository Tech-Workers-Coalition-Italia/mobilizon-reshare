from dataclasses import dataclass, field
from uuid import UUID

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.exceptions import PublisherError
from mobilizon_reshare.publishers.telegram import TelegramPublisher

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
            (publication_id, KEY2CLS[publisher_name](event))
            for publication_id, publisher_name in publications
        )

    def run(self) -> PublisherCoordinatorReport:
        errors = self._validate()
        if errors:
            return PublisherCoordinatorReport(reports=errors)

        return self._post()

    def _make_successful_report(self):
        return {
            publication_id: PublicationReport(
                status=PublicationStatus.COMPLETED, reason="",
            )
            for publication_id, _ in self.publications
        }

    def _post(self):
        failed_publishers_reports = {}
        for publication_id, p in self.publications:
            try:
                p.post()
            except PublisherError as e:
                failed_publishers_reports[publication_id] = PublicationReport(
                    status=PublicationStatus.FAILED, reason=repr(e),
                )
        reports = failed_publishers_reports or self._make_successful_report()
        return PublisherCoordinatorReport(reports)

    def _validate(self):
        errors: dict[UUID, PublicationReport] = {}
        for publication_id, p in self.publications:
            reason = []
            if not p.are_credentials_valid():
                reason.append("Invalid credentials")
            if not p.is_event_valid():
                reason.append("Invalid event")
            if not p.is_message_valid():
                reason.append("Invalid message")

            if len(reason) > 0:
                errors[publication_id] = PublicationReport(
                    status=PublicationStatus.FAILED, reason=", ".join(reason)
                )

        return errors
