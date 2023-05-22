import dataclasses
import logging
from dataclasses import dataclass
from typing import List, Optional, Sequence

from mobilizon_reshare.dataclasses.publication import _EventPublication
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.coordinators import BasePublicationReport

logger = logging.getLogger(__name__)


@dataclass
class EventPublicationReport(BasePublicationReport):
    publication: _EventPublication
    published_content: Optional[str] = dataclasses.field(default=None)

    def get_failure_message(self):
        if not self.reason:
            logger.error("Report of failure without reason.", exc_info=True)

        return (
            f"Publication {self.publication.id} failed with status: {self.status.name}.\n"
            f"Reason: {self.reason}\n"
            f"Publisher: {self.publication.publisher.name}\n"
            f"Event: {self.publication.event.name}"
        )


class BaseEventPublishingCoordinator:
    def __init__(self, publications: List[_EventPublication]):
        self.publications = publications

    def _safe_run(self, reasons, f, *args, **kwargs):
        try:
            f(*args, **kwargs)
            return reasons
        except Exception as e:
            return reasons + [str(e)]

    def _validate(self) -> List[EventPublicationReport]:
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

    def _filter_publications(self, errors: Sequence[EventPublicationReport]) -> List[_EventPublication]:
        publishers_with_errors = set(e.publication.publisher for e in errors)
        return [p for p in self.publications if p.publisher not in publishers_with_errors]
