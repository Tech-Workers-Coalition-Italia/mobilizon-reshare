from enum import IntEnum

from mobilizon_reshare.models.publication import Publication, PublicationStatus


class _EventPublicationStatus(IntEnum):
    WAITING = 1
    FAILED = 2
    COMPLETED = 3
    PARTIAL = 4


def _compute_event_status(publications: list[Publication],) -> _EventPublicationStatus:
    if not publications:
        return _EventPublicationStatus.WAITING

    unique_statuses: set[PublicationStatus] = set(pub.status for pub in publications)

    if unique_statuses == {
        PublicationStatus.COMPLETED,
        PublicationStatus.FAILED,
    }:
        return _EventPublicationStatus.PARTIAL
    elif len(unique_statuses) == 1:
        return _EventPublicationStatus[unique_statuses.pop().name]

    raise ValueError(f"Illegal combination of PublicationStatus: {unique_statuses}")
