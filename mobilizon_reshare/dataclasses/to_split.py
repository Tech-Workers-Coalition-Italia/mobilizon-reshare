from functools import partial
from typing import Optional, Iterator
from uuid import UUID

from arrow import Arrow
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

from mobilizon_reshare.dataclasses import MobilizonEvent, EventPublication
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication, PublicationStatus
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
        # TODO: this is redundant but there's some prefetch problem otherwise
        publication.event = await get_event(publication.event.mobilizon_id)
        return EventPublication.from_orm(
            event=MobilizonEvent.from_model(publication.event), model=publication
        )
    except DoesNotExist:
        return None


async def get_publisher_by_name(name) -> Publisher:
    return await Publisher.filter(name=name).first()


async def get_event_publications(
    mobilizon_event: MobilizonEvent,
) -> list[EventPublication]:
    event = await get_event(mobilizon_event.mobilizon_id)
    return [EventPublication.from_orm(p, mobilizon_event) for p in event.publications]


async def is_known(event: MobilizonEvent) -> bool:
    try:
        await get_event(event.mobilizon_id)
        return True
    except EventNotFound:
        return False


@atomic()
async def build_publications(
    event: MobilizonEvent, publishers: Iterator[str]
) -> list[EventPublication]:
    event_model = await get_event(event.mobilizon_id)
    models = [
        await event_model.build_publication_by_publisher_name(name)
        for name in publishers
    ]
    return [EventPublication.from_orm(m, event) for m in models]


@atomic()
async def get_failed_publications_for_event(
    event_mobilizon_id: UUID,
) -> list[EventPublication]:
    event = await get_event(event_mobilizon_id)
    failed_publications = list(
        filter(
            lambda publications: publications.status == PublicationStatus.FAILED,
            event.publications,
        )
    )
    for p in failed_publications:
        await p.fetch_related("publisher")
    mobilizon_event = MobilizonEvent.from_model(event)
    return list(
        map(
            partial(EventPublication.from_orm, event=mobilizon_event),
            failed_publications,
        )
    )
