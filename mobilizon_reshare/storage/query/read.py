import dataclasses
from functools import partial
from typing import Iterable, Optional
from uuid import UUID

from arrow import Arrow
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet
from tortoise.transactions import atomic

from mobilizon_reshare.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication, PublicationStatus
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers import get_active_publishers
from mobilizon_reshare.publishers.abstract import EventPublication
from mobilizon_reshare.storage.query import CONNECTION_NAME
from mobilizon_reshare.storage.query.converter import (
    event_from_model,
    compute_event_status,
    publication_from_orm,
)
from mobilizon_reshare.storage.query.exceptions import EventNotFound


async def get_published_events(
    from_date: Optional[Arrow] = None, to_date: Optional[Arrow] = None
) -> Iterable[MobilizonEvent]:
    """
    Retrieves events that are not waiting. Function could be renamed to something more fitting
    :return:
    """
    return await events_with_status(
        [
            EventPublicationStatus.COMPLETED,
            EventPublicationStatus.PARTIAL,
            EventPublicationStatus.FAILED,
        ],
        from_date=from_date,
        to_date=to_date,
    )


async def events_with_status(
    status: list[EventPublicationStatus],
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> Iterable[MobilizonEvent]:
    def _filter_event_with_status(event: Event) -> bool:
        # This computes the status client-side instead of running in the DB. It shouldn't pose a performance problem
        # in the short term, but should be moved to the query if possible.
        event_status = compute_event_status(list(event.publications))
        return event_status in status

    query = Event.all()

    return map(
        event_from_model,
        filter(
            _filter_event_with_status,
            await prefetch_event_relations(
                _add_date_window(query, "begin_datetime", from_date, to_date)
            ),
        ),
    )


async def get_all_publications(
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> Iterable[EventPublication]:
    return await prefetch_publication_relations(
        _add_date_window(Publication.all(), "timestamp", from_date, to_date)
    )


async def get_all_events(
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> list[MobilizonEvent]:
    return [
        event_from_model(event)
        for event in await prefetch_event_relations(
            _add_date_window(Event.all(), "begin_datetime", from_date, to_date)
        )
    ]


async def prefetch_event_relations(queryset: QuerySet[Event]) -> list[Event]:
    return (
        await queryset.prefetch_related("publications__publisher")
        .order_by("begin_datetime")
        .distinct()
    )


async def prefetch_publication_relations(
    queryset: QuerySet[Publication],
) -> list[Publication]:
    publication = (
        await queryset.prefetch_related("publisher", "event")
        .order_by("timestamp")
        .distinct()
    )
    return publication


def _add_date_window(
    query,
    field_name: str,
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
):
    if from_date:
        query = query.filter(**{f"{field_name}__gt": from_date.to("utc").datetime})
    if to_date:
        query = query.filter(**{f"{field_name}__lt": to_date.to("utc").datetime})
    return query


@atomic(CONNECTION_NAME)
async def publications_with_status(
    status: PublicationStatus,
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> Iterable[Publication]:
    query = Publication.filter(status=status)

    return await prefetch_publication_relations(
        _add_date_window(query, "timestamp", from_date, to_date)
    )


async def events_without_publications(
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> list[MobilizonEvent]:
    query = Event.filter(publications__id=None)
    events = await prefetch_event_relations(
        _add_date_window(query, "begin_datetime", from_date, to_date)
    )
    return [event_from_model(event) for event in events]


async def get_event(event_mobilizon_id: UUID) -> Event:
    events = await prefetch_event_relations(
        Event.filter(mobilizon_id=event_mobilizon_id)
    )
    if not events:
        raise EventNotFound(f"No event with mobilizon_id {event_mobilizon_id} found.")

    return events[0]


async def get_publisher_by_name(name) -> Publisher:
    return await Publisher.filter(name=name).first()


async def is_known(event: MobilizonEvent) -> bool:
    try:
        await get_event(event.mobilizon_id)
        return True
    except EventNotFound:
        return False


@atomic(CONNECTION_NAME)
async def build_publications(event: MobilizonEvent) -> list[EventPublication]:
    event_model = await get_event(event.mobilizon_id)
    models = [
        await event_model.build_publication_by_publisher_name(name)
        for name in get_active_publishers()
    ]
    return [publication_from_orm(m, dataclasses.replace(event)) for m in models]


@atomic(CONNECTION_NAME)
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
    mobilizon_event = event_from_model(event)
    return list(
        map(partial(publication_from_orm, event=mobilizon_event), failed_publications)
    )


@atomic(CONNECTION_NAME)
async def get_publication(publication_id):
    try:
        publication = await prefetch_publication_relations(
            Publication.get(id=publication_id).first()
        )
        # TODO: this is redundant but there's some prefetch problem otherwise
        publication.event = await get_event(publication.event.mobilizon_id)
        return publication_from_orm(
            event=event_from_model(publication.event), model=publication
        )
    except DoesNotExist:
        return None
