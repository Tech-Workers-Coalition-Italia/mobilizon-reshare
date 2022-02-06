import sys
from typing import Optional
from uuid import UUID

import arrow
import tortoise.timezone

from mobilizon_reshare.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_reshare.models.event import Event

CONNECTION_NAME = "models" if "pytest" in sys.modules else None


def to_model(event: MobilizonEvent, db_id: Optional[UUID] = None) -> Event:
    kwargs = {
        "name": event.name,
        "description": event.description,
        "mobilizon_id": event.mobilizon_id,
        "mobilizon_link": event.mobilizon_link,
        "thumbnail_link": event.thumbnail_link,
        "location": event.location,
        "begin_datetime": event.begin_datetime.astimezone(event.begin_datetime.tzinfo),
        "end_datetime": event.end_datetime.astimezone(event.end_datetime.tzinfo),
        "last_update_time": event.last_update_time.astimezone(
            event.last_update_time.tzinfo
        ),
    }
    if db_id is not None:
        kwargs.update({"id": db_id})
    return Event(**kwargs)


def from_model(event: Event, tz: str = "UTC"):
    publication_status = MobilizonEvent.compute_status(list(event.publications))
    publication_time = {}

    for pub in event.publications:
        if publication_status != EventPublicationStatus.WAITING:
            assert pub.timestamp is not None
            publication_time[pub.publisher.name] = arrow.get(
                tortoise.timezone.localtime(value=pub.timestamp, timezone=tz)
            ).to("local")
    return MobilizonEvent(
        name=event.name,
        description=event.description,
        begin_datetime=arrow.get(
            tortoise.timezone.localtime(value=event.begin_datetime, timezone=tz)
        ).to("local"),
        end_datetime=arrow.get(
            tortoise.timezone.localtime(value=event.end_datetime, timezone=tz)
        ).to("local"),
        mobilizon_link=event.mobilizon_link,
        mobilizon_id=event.mobilizon_id,
        thumbnail_link=event.thumbnail_link,
        location=event.location,
        publication_time=publication_time,
        status=publication_status,
        last_update_time=arrow.get(
            tortoise.timezone.localtime(value=event.last_update_time, timezone=tz)
        ).to("local"),
    )
