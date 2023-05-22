import dataclasses
import logging
from dataclasses import dataclass
from typing import Sequence, List

from mobilizon_reshare.dataclasses.publication import _EventPublication
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.coordinators import BaseCoordinatorReport
from mobilizon_reshare.publishers.coordinators.event_publishing import (
    BaseEventPublishingCoordinator,
    EventPublicationReport,
)
from mobilizon_reshare.publishers.exceptions import PublisherError

logger = logging.getLogger(__name__)


@dataclass
class PublisherCoordinatorReport(BaseCoordinatorReport):
    reports: Sequence[EventPublicationReport]
    publications: Sequence[_EventPublication] = dataclasses.field(default_factory=list)

    def __str__(self):
        platform_messages = []
        for report in self.reports:
            intro = f"Message for: {report.publication.publisher.name}"
            platform_messages.append(
                f"""{intro}
{"*" * len(intro)}
{report.published_content}
{"-" * 80}"""
            )
        return "\n".join(platform_messages)


class PublisherCoordinator(BaseEventPublishingCoordinator):
    """
    Coordinator to publish an event on every active platform
    """

    def run(self) -> PublisherCoordinatorReport:
        validation_reports = self._validate()
        valid_publications = self._filter_publications(validation_reports)
        publishing_reports = self._publish(valid_publications)
        return PublisherCoordinatorReport(
            publications=self.publications,
            reports=validation_reports + publishing_reports
        )

    def _publish(self, publications: Sequence[_EventPublication]) -> List[EventPublicationReport]:
        reports = []

        for publication in publications:

            try:
                publication_report = self._publish_publication(publication)
                reports.append(publication_report)
            except PublisherError as e:
                logger.error(str(e))
                reports.append(
                    EventPublicationReport(
                        status=PublicationStatus.FAILED,
                        reason=str(e),
                        publication=publication,
                    )
                )

        return reports

    @staticmethod
    def _publish_publication(publication):
        """
        Publishes a single publication
        :param publication:
        :return:
        """

        logger.info("Publishing to %s", publication.publisher.name)
        message = publication.formatter.get_message_from_event(publication.event)
        publication.publisher.send(message, publication.event)
        return EventPublicationReport(
            status=PublicationStatus.COMPLETED,
            publication=publication,
            reason=None,
            published_content=message,
        )
