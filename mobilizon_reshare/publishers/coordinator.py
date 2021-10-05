import logging
from dataclasses import dataclass
from typing import List
from uuid import UUID

from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers import get_active_notifiers
from mobilizon_reshare.publishers.abstract import (
    EventPublication,
    AbstractPlatform,
    RecapPublication,
)
from mobilizon_reshare.publishers.exceptions import PublisherError
from mobilizon_reshare.publishers.platforms.platform_mapping import get_notifier_class

logger = logging.getLogger(__name__)


@dataclass
class BasePublicationReport:
    status: PublicationStatus
    reason: str


@dataclass
class PublicationReport(BasePublicationReport):
    publication_id: UUID


@dataclass
class BaseCoordinatorReport:
    reports: dict[UUID, BasePublicationReport]

    @property
    def successful(self):
        return all(
            r.status == PublicationStatus.COMPLETED for r in self.reports.values()
        )


@dataclass
class PublisherCoordinatorReport(BaseCoordinatorReport):
    publications: List[EventPublication]


class PublisherCoordinator:
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
                message = publication.formatter.get_message_from_event(
                    publication.event
                )
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
            if not publication.formatter.is_event_valid(publication.event):
                reason.append("Invalid event")
            if not publication.formatter.is_message_valid(publication.event):
                reason.append("Invalid message")

            if len(reason) > 0:
                errors[publication.id] = PublicationReport(
                    status=PublicationStatus.FAILED,
                    reason=", ".join(reason),
                    publication_id=publication.id,
                )

        return errors


class AbstractCoordinator:
    def __init__(self, message: str, platforms: List[AbstractPlatform] = None):
        self.message = message
        self.platforms = platforms

    def send_to_all(self):
        # TODO: failure to send should fail safely and write to a dedicated log
        for platform in self.platforms:
            platform.send(self.message)


class AbstractNotifiersCoordinator(AbstractCoordinator):
    def __init__(self, message: str, notifiers: List[AbstractPlatform] = None):
        platforms = notifiers or [
            get_notifier_class(notifier)() for notifier in get_active_notifiers()
        ]
        super(AbstractNotifiersCoordinator, self).__init__(message, platforms)


class PublicationFailureNotifiersCoordinator(AbstractNotifiersCoordinator):
    def __init__(self, report: PublicationReport, platforms=None):
        self.report = report
        super(PublicationFailureNotifiersCoordinator, self).__init__(
            message=self.build_failure_message(), notifiers=platforms
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


class RecapCoordinator:
    def __init__(self, recap_publications: List[RecapPublication]):
        self.recap_publications = recap_publications

    def run(self):
        for recap_publication in self.recap_publications:
            fragments = []
            for event in recap_publication.events:
                fragments.append(recap_publication.formatter.get_recap_fragment(event))
            message = "\n\n".join(fragments)
            recap_publication.publisher.send(message)
