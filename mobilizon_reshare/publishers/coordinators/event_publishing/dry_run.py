import logging
from typing import List, Sequence

from mobilizon_reshare.dataclasses import _EventPublication
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    PublisherCoordinator,
    EventPublicationReport,
)

logger = logging.getLogger(__name__)


class DryRunPublisherCoordinator(PublisherCoordinator):
    """
    Coordinator to perform a dry-run on the event publication
    """

    def _publish(self, publications: Sequence[_EventPublication]) -> List[EventPublicationReport]:
        reports = [
            EventPublicationReport(
                status=PublicationStatus.COMPLETED,
                publication=publication,
                reason=None,
                published_content=publication.formatter.get_message_from_event(
                    publication.event
                ),
            )
            for publication in publications
        ]
        logger.info("The following events would be published:")
        for r in reports:
            event_name = r.publication.event.name
            publisher_name = r.publication.publisher.name
            logger.info(f"{event_name} → {publisher_name}")
        return reports
