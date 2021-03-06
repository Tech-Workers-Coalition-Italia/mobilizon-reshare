from datetime import timedelta
from uuid import UUID

from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.models.publication import PublicationStatus
from tests import today

complete_specification = {
    "event": 4,
    "publications": [
        {"event_idx": 0, "publisher_idx": 0, "status": PublicationStatus.COMPLETED},
        {"event_idx": 0, "publisher_idx": 1, "status": PublicationStatus.COMPLETED},
        {"event_idx": 0, "publisher_idx": 2, "status": PublicationStatus.COMPLETED},
        {"event_idx": 1, "publisher_idx": 0, "status": PublicationStatus.FAILED},
        {"event_idx": 1, "publisher_idx": 2, "status": PublicationStatus.COMPLETED},
        {"event_idx": 2, "publisher_idx": 1, "status": PublicationStatus.COMPLETED},
    ],
    "publisher": ["telegram", "twitter", "mastodon", "zulip"],
}


def _make_test_publication(publication_id, status, event_id, publisher_id):
    return Publication(
        id=UUID(int=publication_id),
        status=status,
        timestamp=today + timedelta(hours=publication_id),
        event_id=UUID(int=event_id),
        publisher_id=UUID(int=publisher_id),
    )


result_publication = {
    i: _make_test_publication(
        i,
        publisher_id=publication["publisher_idx"],
        event_id=publication["event_idx"],
        status=publication["status"],
    )
    for i, publication in enumerate(complete_specification["publications"])
}
