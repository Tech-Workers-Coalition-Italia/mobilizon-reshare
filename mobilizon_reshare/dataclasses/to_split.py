from typing import Optional
from uuid import UUID

from arrow import Arrow
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

from mobilizon_reshare.dataclasses import MobilizonEvent, EventPublication
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.storage.query.exceptions import EventNotFound
from mobilizon_reshare.storage.query.read import (
    prefetch_event_relations,
    _add_date_window,
    prefetch_publication_relations,
    get_event,
)


async def events_without_publications(
    from_date: Optional[Arrow] = None, to_date: Optional[Arrow] = None,
) -> list[MobilizonEvent]:
    query = Event.filter(publications__id=None)
    events = await prefetch_event_relations(
        _add_date_window(query, "begin_datetime", from_date, to_date)
    )
    return [MobilizonEvent.from_model(event) for event in events]


@atomic()
async def get_publication(publication_id: UUID):
    try:
        publication = await prefetch_publication_relations(
            Publication.get(id=publication_id).first()
        )
        return EventPublication.from_orm(
            event=MobilizonEvent.from_model(publication.event), model=publication
        )
    except DoesNotExist:
        return None


async def get_publisher_by_name(name) -> Publisher:
    return await Publisher.filter(name=name).first()


async def is_known(event: MobilizonEvent) -> bool:
    try:
        await get_event(event.mobilizon_id)
        return True
    except EventNotFound:
        return False
