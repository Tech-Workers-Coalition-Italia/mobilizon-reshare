from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.coordinators.event_publishing import (
    BaseEventPublishingCoordinator,
)
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    PublisherCoordinatorReport,
    EventPublicationReport,
)


class DryRunPublisherCoordinator(BaseEventPublishingCoordinator):
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
