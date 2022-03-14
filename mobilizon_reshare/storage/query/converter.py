from typing import Optional
from uuid import UUID

import arrow
import tortoise.timezone

from mobilizon_reshare.event.event import EventPublicationStatus, MobilizonEvent
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication, PublicationStatus
from mobilizon_reshare.publishers.abstract import EventPublication


def event_from_model(event: Event):

    publication_status = compute_event_status(list(event.publications))
    publication_time = {}

    for pub in event.publications:
        if publication_status != EventPublicationStatus.WAITING:
            assert pub.timestamp is not None
            publication_time[pub.publisher.name] = arrow.get(pub.timestamp).to("local")
    return MobilizonEvent(
        name=event.name,
        description=event.description,
        begin_datetime=arrow.get(event.begin_datetime).to("local"),
        end_datetime=arrow.get(event.end_datetime).to("local"),
        mobilizon_link=event.mobilizon_link,
        mobilizon_id=event.mobilizon_id,
        thumbnail_link=event.thumbnail_link,
        location=event.location,
        publication_time=publication_time,
        status=publication_status,
        last_update_time=arrow.get(event.last_update_time).to("local"),
    )


def event_to_model(event: MobilizonEvent, db_id: Optional[UUID] = None) -> Event:
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


def compute_event_status(publications: list[Publication]) -> EventPublicationStatus:
    if not publications:
        return EventPublicationStatus.WAITING

    unique_statuses: set[PublicationStatus] = set(pub.status for pub in publications)

    if unique_statuses == {
        PublicationStatus.COMPLETED,
        PublicationStatus.FAILED,
    }:
        return EventPublicationStatus.PARTIAL
    elif len(unique_statuses) == 1:
        return EventPublicationStatus[unique_statuses.pop().name]

    raise ValueError(f"Illegal combination of PublicationStatus: {unique_statuses}")


def publication_from_orm(model: Publication, event: MobilizonEvent) -> EventPublication:
    # imported here to avoid circular dependencies
    from mobilizon_reshare.publishers.platforms.platform_mapping import (
        get_publisher_class,
        get_formatter_class,
    )

    publisher = get_publisher_class(model.publisher.name)()
    formatter = get_formatter_class(model.publisher.name)()
    return EventPublication(publisher, formatter, event, model.id,)
