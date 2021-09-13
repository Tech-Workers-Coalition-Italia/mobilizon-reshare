import logging
from dataclasses import dataclass, field
from uuid import UUID

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers import get_active_notifiers, get_active_publishers
from mobilizon_reshare.publishers.abstract import AbstractPublisher
from mobilizon_reshare.publishers.exceptions import PublisherError
from mobilizon_reshare.publishers.telegram import TelegramPublisher
from mobilizon_reshare.publishers.zulip import ZulipPublisher

logger = logging.getLogger(__name__)

name_to_publisher_class = {"telegram": TelegramPublisher, "zulip": ZulipPublisher}


class BuildPublisherMixin:
    @staticmethod
    def build_publishers(
        event: MobilizonEvent, publisher_names
    ) -> dict[str, AbstractPublisher]:

        return {
            publisher_name: name_to_publisher_class[publisher_name](event)
            for publisher_name in publisher_names
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


class PublisherCoordinator(BuildPublisherMixin):
    def __init__(self, event: MobilizonEvent, publications: dict[UUID, Publication]):
        publishers = self.build_publishers(event, get_active_publishers())
        self.publishers_by_publication_id = {
            publication_id: publishers[publication.publisher.name]
            for publication_id, publication in publications.items()
        }

    def run(self) -> PublisherCoordinatorReport:
        errors = self._validate()
        if errors:
            return PublisherCoordinatorReport(
                reports=errors, publishers=self.publishers_by_publication_id
            )

        return self._post()

    def _make_successful_report(self, failed_ids):
        return {
            publication_id: PublicationReport(
                status=PublicationStatus.COMPLETED,
                reason="",
                publication_id=publication_id,
            )
            for publication_id in self.publishers_by_publication_id
            if publication_id not in failed_ids
        }

    def _post(self):
        failed_publishers_reports = {}
        for publication_id, p in self.publishers_by_publication_id.items():
            try:
                p.publish()
            except PublisherError as e:
                failed_publishers_reports[publication_id] = PublicationReport(
                    status=PublicationStatus.FAILED,
                    reason=str(e),
                    publication_id=publication_id,
                )

        reports = failed_publishers_reports | self._make_successful_report(
            failed_publishers_reports.keys()
        )
        return PublisherCoordinatorReport(
            publishers=self.publishers_by_publication_id, reports=reports
        )

    def _validate(self):
        errors: dict[UUID, PublicationReport] = {}
        for publication_id, p in self.publishers_by_publication_id.items():
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

    @staticmethod
    def get_formatted_message(event: MobilizonEvent, publisher: str) -> str:
        """
        Returns the formatted message for a given event and publisher.
        """
        if publisher not in name_to_publisher_class:
            raise ValueError(
                f"Publisher {publisher} does not exist.\nSupported publishers: "
                f"{', '.join(list(name_to_publisher_class.keys()))}"
            )

        return name_to_publisher_class[publisher](event).get_message_from_event()


class AbstractNotifiersCoordinator(BuildPublisherMixin):
    def __init__(self, event: MobilizonEvent):
        self.event = event
        self.notifiers = self.build_publishers(event, get_active_notifiers())

    def send_to_all(self, message):
        # TODO: failure to notify should fail safely and write to a dedicated log
        for notifier in self.notifiers.values():
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
