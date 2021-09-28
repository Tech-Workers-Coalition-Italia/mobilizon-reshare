import logging
from dataclasses import dataclass, field
from typing import List
from uuid import UUID

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import (
    PublicationStatus,
    Publication as PublicationModel,
)
from mobilizon_reshare.publishers import get_active_notifiers
from mobilizon_reshare.publishers.abstract import AbstractNotifier, EventPublication
from mobilizon_reshare.publishers.exceptions import PublisherError
from mobilizon_reshare.publishers.platforms import name_to_publisher_class

logger = logging.getLogger(__name__)


class BuildPublisherMixin:
    @staticmethod
    def build_notifier(message: str, publisher_names) -> dict[str, AbstractNotifier]:

        return {
            publisher_name: name_to_publisher_class[publisher_name](message=message)
            for publisher_name in publisher_names
        }


@dataclass
class PublicationReport:
    status: PublicationStatus
    reason: str
    publication_id: UUID


@dataclass
class PublisherCoordinatorReport:
    publications: List[EventPublication]
    reports: dict[UUID, PublicationReport] = field(default_factory={})

    @property
    def successful(self):
        return all(
            r.status == PublicationStatus.COMPLETED for r in self.reports.values()
        )


class PublisherCoordinator(BuildPublisherMixin):
    def __init__(self, publications: List[EventPublication]):
        self.publications = publications

    def run(self) -> PublisherCoordinatorReport:
        errors = self._validate()
        if errors:
            return PublisherCoordinatorReport(
                reports=errors, publications=self.publications
            )

        return self._post()

    def _make_successful_report(self, failed_ids):
        return {
            publication.id: PublicationReport(
                status=PublicationStatus.COMPLETED,
                reason="",
                publication_id=publication.id,
            )
            for publication in self.publications
            if publication.id not in failed_ids
        }

    def _post(self):
        failed_publishers_reports = {}
        for publication in self.publications:
            try:
                message = publication.formatter.get_message_from_event()
                publication.publisher.send(message)
            except PublisherError as e:
                failed_publishers_reports[publication.id] = PublicationReport(
                    status=PublicationStatus.FAILED,
                    reason=str(e),
                    publication_id=publication.id,
                )

        reports = failed_publishers_reports | self._make_successful_report(
            failed_publishers_reports.keys()
        )
        return PublisherCoordinatorReport(
            publications=self.publications, reports=reports
        )

    def _validate(self):
        errors: dict[UUID, PublicationReport] = {}
        for publication in self.publications:
            reason = []
            if not publication.publisher.are_credentials_valid():
                reason.append("Invalid credentials")
            if not publication.formatter.is_event_valid():
                reason.append("Invalid event")
            if not publication.formatter.is_message_valid():
                reason.append("Invalid message")

            if len(reason) > 0:
                errors[publication.id] = PublicationReport(
                    status=PublicationStatus.FAILED,
                    reason=", ".join(reason),
                    publication_id=publication.id,
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
    def __init__(self, message: str, notifiers=None):
        if notifiers:
            self.notifiers = notifiers
        else:
            self.notifiers = self.build_notifier(message, get_active_notifiers())

    def send_to_all(self):
        # TODO: failure to notify should fail safely and write to a dedicated log
        for notifier in self.notifiers.values():
            notifier.send()


class PublicationFailureNotifiersCoordinator(AbstractNotifiersCoordinator):
    def __init__(self, report: PublicationReport, notifiers=None):
        self.report = report
        super(PublicationFailureNotifiersCoordinator, self).__init__(
            message=self.build_failure_message(), notifiers=notifiers
        )

    def build_failure_message(self):
        report = self.report
        return (
            f"Publication {report.publication_id} failed with status: {report.status}.\n"
            f"Reason: {report.reason}"
        )

    def notify_failure(self):
        logger.info(
            f"Sending failure notifications for publication: {self.report.publication_id}"
        )
        if self.report.status == PublicationStatus.FAILED:
            self.send_to_all()
