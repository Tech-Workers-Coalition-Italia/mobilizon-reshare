from datetime import timedelta
from uuid import UUID

import arrow

from mobilizon_reshare.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.models.publication import PublicationStatus
from tests import today

event_0 = MobilizonEvent(
    name="event_0",
    description="desc_0",
    mobilizon_id=UUID(int=0),
    mobilizon_link="moblink_0",
    thumbnail_link="thumblink_0",
    location="loc_0",
    status=EventPublicationStatus.WAITING,
    begin_datetime=arrow.get(today),
    end_datetime=arrow.get(today + timedelta(hours=2)),
    last_update_time=arrow.get(today),
)

event_1 = MobilizonEvent(
    name="event_1",
    description="desc_1",
    mobilizon_id=UUID(int=1),
    mobilizon_link="moblink_1",
    thumbnail_link="thumblink_1",
    location="loc_1",
    status=EventPublicationStatus.WAITING,
    begin_datetime=arrow.get(today + timedelta(days=1)),
    end_datetime=arrow.get(today + timedelta(days=1) + timedelta(hours=2)),
    last_update_time=arrow.get(today + timedelta(days=1)),
)

event_2 = MobilizonEvent(
    name="event_2",
    description="desc_2",
    mobilizon_id=UUID(int=2),
    mobilizon_link="moblink_2",
    thumbnail_link="thumblink_2",
    location="loc_2",
    status=EventPublicationStatus.WAITING,
    begin_datetime=arrow.get(today + timedelta(days=2)),
    end_datetime=arrow.get(today + timedelta(days=2) + timedelta(hours=2)),
    last_update_time=arrow.get(today + timedelta(days=2)),
)

event_3 = MobilizonEvent(
    name="event_3",
    description="desc_3",
    mobilizon_id=UUID(int=3),
    mobilizon_link="moblink_3",
    thumbnail_link="thumblink_3",
    location="loc_3",
    status=EventPublicationStatus.WAITING,
    begin_datetime=arrow.get(today + timedelta(days=3)),
    end_datetime=arrow.get(today + timedelta(days=3) + timedelta(hours=2)),
    last_update_time=arrow.get(today + timedelta(days=3)),
)

event_3_updated = MobilizonEvent(
    name="event_3",
    description="desc_3",
    mobilizon_id=UUID(int=3),
    mobilizon_link="moblink_3",
    thumbnail_link="thumblink_3",
    location="loc_6",
    status=EventPublicationStatus.WAITING,
    begin_datetime=arrow.get(today + timedelta(days=3)),
    end_datetime=arrow.get(today + timedelta(days=3) + timedelta(hours=2)),
    last_update_time=arrow.get(today + timedelta(days=4)),
)

event_6 = MobilizonEvent(
    name="event_6",
    description="desc_6",
    mobilizon_id=UUID(int=6),
    mobilizon_link="moblink_6",
    thumbnail_link="thumblink_6",
    location="loc_6",
    status=EventPublicationStatus.WAITING,
    begin_datetime=arrow.get(today + timedelta(days=6)),
    end_datetime=arrow.get(today + timedelta(days=6) + timedelta(hours=2)),
    last_update_time=arrow.get(today + timedelta(days=6)),
)

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
