import sys
from typing import Optional
from uuid import UUID

from mobilizon_reshare.event.event import MobilizonEvent
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
