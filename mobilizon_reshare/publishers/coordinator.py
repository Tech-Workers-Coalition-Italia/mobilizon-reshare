import logging
from dataclasses import dataclass
from typing import List, Optional
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
    reason: Optional[str]

    def get_failure_message(self):

        return (
            f"Publication failed with status: {self.status}.\n" f"Reason: {self.reason}"
        )


@dataclass
class EventPublicationReport(BasePublicationReport):
    publication_id: UUID

    def get_failure_message(self):

        return (
            f"Publication {self.publication_id } failed with status: {self.status}.\n"
            f"Reason: {self.reason}"
        )


@dataclass
class BaseCoordinatorReport:
    reports: List[BasePublicationReport]

    @property
    def successful(self):
        return all(r.status == PublicationStatus.COMPLETED for r in self.reports)


@dataclass
class PublisherCoordinatorReport(BaseCoordinatorReport):

    reports: List[EventPublicationReport]
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
        return [
            EventPublicationReport(
                status=PublicationStatus.COMPLETED,
                reason="",
                publication_id=publication.id,
            )
            for publication in self.publications
            if publication.id not in failed_ids
        ]

    def _post(self):
        reports = []

        for publication in self.publications:

            try:
                message = publication.formatter.get_message_from_event(
                    publication.event
                )
                publication.publisher.send(message)
                reports.append(
                    EventPublicationReport(
                        status=PublicationStatus.COMPLETED,
                        publication_id=publication.id,
                        reason=None,
                    )
                )
            except PublisherError as e:
                reports.append(
                    EventPublicationReport(
                        status=PublicationStatus.FAILED,
                        reason=str(e),
                        publication_id=publication.id,
                    )
                )

        return PublisherCoordinatorReport(
            publications=self.publications, reports=reports
        )

    def _validate(self):
        errors = []

        for publication in self.publications:

            reason = []
            if not publication.publisher.are_credentials_valid():
                reason.append("Invalid credentials")
            if not publication.formatter.is_event_valid(publication.event):
                reason.append("Invalid event")
            if not publication.formatter.is_message_valid(publication.event):
                reason.append("Invalid message")

            if len(reason) > 0:
                errors.append(
                    EventPublicationReport(
                        status=PublicationStatus.FAILED,
                        reason=", ".join(reason),
                        publication_id=publication.id,
                    )
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
    def __init__(self, report: EventPublicationReport, platforms=None):
        self.report = report
        super(PublicationFailureNotifiersCoordinator, self).__init__(
            message=report.get_failure_message(), notifiers=platforms
        )

    def notify_failure(self):
        logger.info("Sending failure notifications")
        if self.report.status == PublicationStatus.FAILED:
            self.send_to_all()


class RecapCoordinator:
    def __init__(self, recap_publications: List[RecapPublication]):
        self.recap_publications = recap_publications

    def run(self):
        reports = []
        for recap_publication in self.recap_publications:
            try:

                fragments = []
                for event in recap_publication.events:
                    fragments.append(
                        recap_publication.formatter.get_recap_fragment(event)
                    )
                message = "\n\n".join(fragments)
                recap_publication.publisher.send(message)
                reports.append(
                    BasePublicationReport(
                        status=PublicationStatus.COMPLETED, reason=None,
                    )
                )
            except PublisherError as e:
                reports.append(
                    BasePublicationReport(
                        status=PublicationStatus.FAILED, reason=str(e),
                    )
                )

        return BaseCoordinatorReport(reports=reports)
