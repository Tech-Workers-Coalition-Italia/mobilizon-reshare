import dataclasses
from dataclasses import dataclass
from typing import Optional, Sequence, List

from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.dataclasses.publication import RecapPublication
from mobilizon_reshare.publishers.coordinators import (
    BasePublicationReport,
    BaseCoordinatorReport,
)
from mobilizon_reshare.publishers.exceptions import PublisherError


@dataclass
class RecapPublicationReport(BasePublicationReport):
    publication: RecapPublication
    published_content: Optional[str] = dataclasses.field(default=None)


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


class RecapCoordinator:
    """
    Coordinator to publish a recap on future events
    """

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
