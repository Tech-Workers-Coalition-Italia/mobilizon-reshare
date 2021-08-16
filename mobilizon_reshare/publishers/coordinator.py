import logging
from dataclasses import dataclass, field
from uuid import UUID

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers import get_active_notifiers
from mobilizon_reshare.publishers.abstract import AbstractPublisher
from mobilizon_reshare.publishers.exceptions import PublisherError
from mobilizon_reshare.publishers.telegram import TelegramPublisher

logger = logging.getLogger(__name__)


# TODO: find a way to avoid using this map in order to simplify adding more publishers
name_to_publisher_class = {"telegram": TelegramPublisher}


def build_publishers(
    event: MobilizonEvent, publications: dict[UUID, Publication]
) -> dict[UUID, AbstractPublisher]:
    return {
        publication_id: name_to_publisher_class[publication.publisher.name](event)
        for publication_id, publication in publications.items()
    }


@dataclass
class PublicationReport:
    status: PublicationStatus
    reason: str
    publication_id: UUID


@dataclass
class PublisherCoordinatorReport:
    publishers: dict[UUID, AbstractPublisher]
    reports: dict[UUID, PublicationReport] = field(default_factory={})

    @property
    def successful(self):
        return all(
            r.status == PublicationStatus.COMPLETED for r in self.reports.values()
        )


class PublisherCoordinator:
    def __init__(self, event: MobilizonEvent, publications: dict[UUID, Publication]):
        self.publishers = build_publishers(event, publications)

    def run(self) -> PublisherCoordinatorReport:
        errors = self._validate()
        if errors:
            return PublisherCoordinatorReport(
                reports=errors, publishers=self.publishers
            )

        return self._post()

    def _make_successful_report(self):
        return {
            publication_id: PublicationReport(
                status=PublicationStatus.COMPLETED,
                reason="",
                publication_id=publication_id,
            )
            for publication_id in self.publishers
        }

    def _post(self):
        failed_publishers_reports = {}
        for publication_id, p in self.publishers.items():
            try:
                p.publish()
            except PublisherError as e:
                failed_publishers_reports[publication_id] = PublicationReport(
                    status=PublicationStatus.FAILED,
                    reason=repr(e),
                    publication_id=publication_id,
                )

        reports = failed_publishers_reports or self._make_successful_report()
        return PublisherCoordinatorReport(publishers=self.publishers, reports=reports)

    def _validate(self):
        errors: dict[UUID, PublicationReport] = {}
        for publication_id, p in self.publishers.items():
            reason = []
            if not p.are_credentials_valid():
                reason.append("Invalid credentials")
            if not p.is_event_valid():
                reason.append("Invalid event")
            if not p.is_message_valid():
                reason.append("Invalid message")

            if len(reason) > 0:
                errors[publication_id] = PublicationReport(
                    status=PublicationStatus.FAILED,
                    reason=", ".join(reason),
                    publication_id=publication_id,
                )

        return errors


class AbstractNotifiersCoordinator:
    def __init__(self, event: MobilizonEvent):
        self.event = event

    def send_to_all(self, message):
        # TODO: failure to notify should fail safely and write to a dedicated log
        for notifier_name in get_active_notifiers():
            notifier = name_to_publisher_class[notifier_name](self.event)
            notifier.send(message)


class PublicationFailureNotifiersCoordinator(AbstractNotifiersCoordinator):
    def __init__(
        self,
        event: MobilizonEvent,
        publisher_coordinator_report: PublisherCoordinatorReport,
    ):
        self.report = publisher_coordinator_report
        super(PublicationFailureNotifiersCoordinator, self).__init__(event)

    def build_failure_message(self, report: PublicationReport):
        return (
            f"Publication {report.publication_id} failed with status: {report.status}.\n"
            f"Reason: {report.reason}"
        )

    def notify_failures(self):
        for publication_id, report in self.report.reports.items():

            logger.info(
                f"Sending failure notifications for publication: {publication_id}"
            )
            if report.status == PublicationStatus.FAILED:
                self.send_to_all(self.build_failure_message(report))
