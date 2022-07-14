import dataclasses
from dataclasses import dataclass
from typing import Optional, Sequence, List

from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.abstract import EventPublication
from mobilizon_reshare.publishers.coordinators import (
    BasePublicationReport,
    BaseCoordinatorReport,
    logger,
)
from mobilizon_reshare.publishers.exceptions import PublisherError


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
