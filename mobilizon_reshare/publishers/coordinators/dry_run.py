from typing import List

from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.abstract import EventPublication
from mobilizon_reshare.publishers.coordinators.publish import (
    PublisherCoordinator,
    PublisherCoordinatorReport,
    EventPublicationReport,
)
from mobilizon_reshare.publishers.coordinators.recap import RecapCoordinator


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


class DryRunRecapCoordinator(RecapCoordinator):
    def _send(self, content, recap_publication):
        pass
