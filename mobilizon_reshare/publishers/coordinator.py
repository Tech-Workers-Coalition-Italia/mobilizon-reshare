import dataclasses
import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List, Optional, Sequence

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
class RecapPublicationReport(BasePublicationReport):
    publication: RecapPublication
    published_content: Optional[str] = dataclasses.field(default=None)


@dataclass
class EventPublicationReport(BasePublicationReport):
    publication: EventPublication
    published_content: Optional[str] = dataclasses.field(default=None)

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
    reports: Sequence[BasePublicationReport]

    @property
    def successful(self):
        return all(r.status == PublicationStatus.COMPLETED for r in self.reports)


@dataclass
class RecapCoordinatorReport(BaseCoordinatorReport):
    reports: Sequence[RecapPublicationReport]

    def __str__(self):
        platform_messages = []
        for report in self.reports:
            intro = f"Message for: {report.publication.publisher.name}"
            platform_messages.append(
                f"""{intro}
{"*"*len(intro)}
{report.published_content}
{"-"*80}"""
            )
        return "\n".join(platform_messages)


@dataclass
class PublisherCoordinatorReport(BaseCoordinatorReport):
    reports: Sequence[EventPublicationReport]
    publications: Sequence[EventPublication] = dataclasses.field(default_factory=list)

    def __str__(self):
        platform_messages = []
        for report in self.reports:
            intro = f"Message for: {report.publication.publisher.name}"
            platform_messages.append(
                f"""{intro}
{"*"*len(intro)}
{report.published_content}
{"-"*80}"""
            )
        return "\n".join(platform_messages)


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
                        published_content=message,
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


class DryRunPublisherCoordinator(PublisherCoordinator):
    def __init__(self, publications: List[EventPublication]):
        self.publications = publications

    def run(self) -> PublisherCoordinatorReport:
        errors = self._validate()
        if errors:
            coord_report = PublisherCoordinatorReport(
                reports=errors, publications=self.publications
            )
        else:
            reports = [
                EventPublicationReport(
                    status=PublicationStatus.COMPLETED,
                    publication=publication,
                    reason=None,
                    published_content=publication.formatter.get_message_from_event(
                        publication.event
                    ),
                )
                for publication in self.publications
            ]
            coord_report = PublisherCoordinatorReport(
                publications=self.publications, reports=reports
            )

        return coord_report


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
    def __init__(
        self, report: EventPublicationReport, notifiers: List[AbstractPlatform] = None
    ):
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

    def _build_recap_content(self, recap_publication: RecapPublication):
        fragments = [recap_publication.formatter.get_recap_header()]
        for event in recap_publication.events:
            fragments.append(recap_publication.formatter.get_recap_fragment(event))
        return "\n\n".join(fragments)

    def _send(self, content, recap_publication):
        recap_publication.publisher.send(content)

    def run(self) -> RecapCoordinatorReport:
        reports = []
        for recap_publication in self.recap_publications:
            try:

                message = self._build_recap_content(recap_publication)
                self._send(message, recap_publication)
                reports.append(
                    RecapPublicationReport(
                        status=PublicationStatus.COMPLETED,
                        reason=None,
                        published_content=message,
                        publication=recap_publication,
                    )
                )
            except PublisherError as e:
                reports.append(
                    RecapPublicationReport(
                        status=PublicationStatus.FAILED,
                        reason=str(e),
                        publication=recap_publication,
                    )
                )

        return RecapCoordinatorReport(reports=reports)


class DryRunRecapCoordinator(RecapCoordinator):
    def _send(self, content, recap_publication):
        pass
