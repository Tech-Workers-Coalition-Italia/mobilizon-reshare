from typing import Iterable, Optional
from uuid import UUID

from arrow import Arrow
from tortoise.queryset import QuerySet
from tortoise.transactions import atomic

from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication, PublicationStatus
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.storage.query.exceptions import EventNotFound


async def get_all_publications(
    from_date: Optional[Arrow] = None, to_date: Optional[Arrow] = None,
) -> Iterable[Publication]:
    return await prefetch_publication_relations(
        _add_date_window(Publication.all(), "timestamp", from_date, to_date)
    )


async def get_all_events(
    from_date: Optional[Arrow] = None, to_date: Optional[Arrow] = None
):
    return await prefetch_event_relations(
        _add_date_window(Event.all(), "begin_datetime", from_date, to_date)
    )


async def get_all_publishers() -> list[Publisher]:
    return await Publisher.all()


async def prefetch_event_relations(queryset: QuerySet[Event]) -> list[Event]:
    return (
        await queryset.prefetch_related("publications__publisher", "publications__notifications")
        .order_by("begin_datetime")
        .distinct()
    )


async def prefetch_publication_relations(
    queryset: QuerySet[Publication],
) -> list[Publication]:
    publication = (
        await queryset.prefetch_related(
            "publisher",
            "event",
            "notifications",
            "event__publications",
            "event__publications__publisher",
        )
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


@atomic()
async def publications_with_status(
    status: PublicationStatus,
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> Iterable[Publication]:
    query = Publication.filter(status=status)

    return await prefetch_publication_relations(
        _add_date_window(query, "timestamp", from_date, to_date)
    )


async def get_event(event_mobilizon_id: UUID) -> Event:
    events = await prefetch_event_relations(
        Event.filter(mobilizon_id=event_mobilizon_id)
    )
    if not events:
        raise EventNotFound(f"No event with mobilizon_id {event_mobilizon_id} found.")

    return events[0]


async def get_events_without_publications(
    from_date: Optional[Arrow] = None, to_date: Optional[Arrow] = None,
) -> list[Event]:
    query = Event.filter(publications__id=None)
    return await prefetch_event_relations(
        _add_date_window(query, "begin_datetime", from_date, to_date)
    )
