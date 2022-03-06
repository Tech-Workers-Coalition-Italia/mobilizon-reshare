import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List, Optional

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

    @property
    def succesful(self):
        return self.status == PublicationStatus.COMPLETED

    def get_failure_message(self):

        return (
            f"Publication failed with status: {self.status}.\n" f"Reason: {self.reason}"
        )


@dataclass
class EventPublicationReport(BasePublicationReport):
    publication: EventPublication

    def get_failure_message(self):

        if not self.reason:
            logger.error("Report of failure without reason.", exc_info=True)

        return (
            f"Publication {self.publication.id} failed with status: {self.status}.\n"
            f"Reason: {self.reason}\n"
            f"Publisher: {self.publication.publisher.name}\n"
            f"Event: {self.publication.event.name}"
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

    def _post(self) -> PublisherCoordinatorReport:
        reports = []

        for publication in self.publications:

            try:
                logger.info(f"Publishing to {publication.publisher.name}")
                message = publication.formatter.get_message_from_event(
                    publication.event
                )
                publication.publisher.send(message, publication.event)
                reports.append(
                    EventPublicationReport(
                        status=PublicationStatus.COMPLETED,
                        publication=publication,
                        reason=None,
                    )
                )
            except PublisherError as e:
                logger.error(str(e))
                reports.append(
                    EventPublicationReport(
                        status=PublicationStatus.FAILED,
                        reason=str(e),
                        publication=publication,
                    )
                )

        return PublisherCoordinatorReport(
            publications=self.publications, reports=reports
        )

    def _safe_run(self, reasons, f, *args, **kwargs):
        try:
            f(*args, **kwargs)
            return reasons
        except Exception as e:
            return reasons + [str(e)]

    def _validate(self):
        errors = []

        for publication in self.publications:
            reasons = []
            reasons = self._safe_run(
                reasons, publication.publisher.validate_credentials,
            )
            reasons = self._safe_run(
                reasons, publication.formatter.validate_event, publication.event
            )

            if len(reasons) > 0:
                errors.append(
                    EventPublicationReport(
                        status=PublicationStatus.FAILED,
                        reason=", ".join(reasons),
                        publication=publication,
                    )
                )

        return errors


class Sender:
    def __init__(self, message: str, platforms: List[AbstractPlatform] = None):
        self.message = message
        self.platforms = platforms

    def send_to_all(self):
        for platform in self.platforms:
            try:
                platform.send(self.message)
            except Exception as e:
                logger.critical(f"Failed to send message:\n{self.message}")
                logger.exception(e)


class AbstractNotifiersCoordinator(ABC):
    def __init__(self, report, notifiers: List[AbstractPlatform] = None):
        self.platforms = notifiers or [
            get_notifier_class(notifier)() for notifier in get_active_notifiers()
        ]
        self.report = report

    @abstractmethod
    def notify_failure(self):
        pass


class PublicationFailureNotifiersCoordinator(AbstractNotifiersCoordinator):
    """
    Sends a notification of a failure report to the active platforms
    """

    def notify_failure(self):
        logger.info("Sending failure notifications")
        if self.report.status == PublicationStatus.FAILED:
            Sender(self.report.get_failure_message(), self.platforms).send_to_all()


class PublicationFailureLoggerCoordinator(PublicationFailureNotifiersCoordinator):
    """
    Logs a report to console
    """

    def notify_failure(self):
        if self.report.status == PublicationStatus.FAILED:
            logger.error(self.report.get_failure_message())


class RecapCoordinator:
    def __init__(self, recap_publications: List[RecapPublication]):
        self.recap_publications = recap_publications

    def run(self) -> BaseCoordinatorReport:
        reports = []
        for recap_publication in self.recap_publications:
            try:

                fragments = [recap_publication.formatter.get_recap_header()]
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
