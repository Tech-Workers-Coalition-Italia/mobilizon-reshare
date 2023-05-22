from typing import List, Sequence

from mobilizon_reshare.dataclasses import _EventPublication
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    PublisherCoordinator,
    EventPublicationReport,
)


class DryRunPublisherCoordinator(PublisherCoordinator):
    """
    Coordinator to perform a dry-run on the event publication
    """

    def _publish(self, publications: Sequence[_EventPublication]) -> List[EventPublicationReport]:
        return [
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
