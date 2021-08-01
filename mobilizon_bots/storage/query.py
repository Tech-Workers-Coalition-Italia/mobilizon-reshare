import logging
import sys
from typing import Iterable, Optional, Union
from uuid import UUID

import arrow
from arrow import Arrow
from tortoise.queryset import QuerySet
from tortoise.transactions import atomic

from mobilizon_bots.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import Publication, PublicationStatus
from mobilizon_bots.models.publisher import Publisher
from mobilizon_bots.publishers.coordinator import PublisherCoordinatorReport

logger = logging.getLogger(__name__)

# This is due to Tortoise community fixtures to
# set up and tear down a DB instance for Pytest.
# See: https://github.com/tortoise/tortoise-orm/issues/419#issuecomment-696991745
# and: https://docs.pytest.org/en/stable/example/simple.html

CONNECTION_NAME = "models" if "pytest" in sys.modules else None


async def prefetch_event_relations(queryset: QuerySet[Event]) -> list[Event]:
    return (
        await queryset.prefetch_related("publications__publisher")
        .order_by("begin_datetime")
        .distinct()
    )


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
    event_mobilizon_id: Optional[UUID] = None,
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> Iterable[Publication]:
    query = Publication.filter(status=status)

    if event_mobilizon_id:
        query = query.prefetch_related("event").filter(
            event__mobilizon_id=event_mobilizon_id
        )

    query = _add_date_window(query, "timestamp", from_date, to_date)

    return await query.prefetch_related("publisher").order_by("timestamp").distinct()


async def events_with_status(
    status: list[EventPublicationStatus],
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> Iterable[MobilizonEvent]:
    def _filter_event_with_status(event: Event) -> bool:
        # This computes the status client-side instead of running in the DB. It shouldn't pose a performance problem
        # in the short term, but should be moved to the query if possible.
        event_status = MobilizonEvent.compute_status(list(event.publications))
        return event_status in status

    query = Event.all()

    return map(
        MobilizonEvent.from_model,
        filter(
            _filter_event_with_status,
            await prefetch_event_relations(
                _add_date_window(query, "begin_datetime", from_date, to_date)
            ),
        ),
    )


async def get_all_events(
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> Iterable[MobilizonEvent]:

    return map(
        MobilizonEvent.from_model,
        await prefetch_event_relations(
            _add_date_window(Event.all(), "begin_datetime", from_date, to_date)
        ),
    )


async def get_published_events() -> Iterable[MobilizonEvent]:
    return await events_with_status([EventPublicationStatus.COMPLETED])


async def get_unpublished_events() -> Iterable[MobilizonEvent]:
    return await events_with_status([EventPublicationStatus.WAITING])


async def get_mobilizon_event_publications(
    event: MobilizonEvent,
) -> Iterable[Publication]:
    models = await prefetch_event_relations(
        Event.filter(mobilizon_id=event.mobilizon_id)
    )
    return models[0].publications


async def get_publishers(
    name: Optional[str] = None,
) -> Union[Publisher, Iterable[Publisher]]:
    if name:
        return await Publisher.filter(name=name).first()
    else:
        return await Publisher.all()


async def save_event(event: MobilizonEvent) -> Event:

    event_model = event.to_model()
    await event_model.save()
    return event_model


async def create_publisher(name: str, account_ref: Optional[str] = None) -> None:
    await Publisher.create(name=name, account_ref=account_ref)


@atomic(CONNECTION_NAME)
async def update_publishers(
    names: Iterable[str],
) -> None:
    names = set(names)
    known_publisher_names = set(p.name for p in await get_publishers())
    for name in names.difference(known_publisher_names):
        logging.info(f"Creating {name} publisher")
        await create_publisher(name)


@atomic(CONNECTION_NAME)
async def save_publication(
    publisher_name: str, event_model: Event, status: PublicationStatus
) -> None:

    publisher = await get_publishers(publisher_name)
    await Publication.create(
        status=status,
        event_id=event_model.id,
        publisher_id=publisher.id,
    )


@atomic(CONNECTION_NAME)
async def create_unpublished_events(
    unpublished_mobilizon_events: Iterable[MobilizonEvent],
    active_publishers: Iterable[str],
) -> None:
    # We store only new events, i.e. events whose mobilizon_id wasn't found in the DB.
    unpublished_event_models = set(
        map(lambda event: event.mobilizon_id, await get_unpublished_events())
    )
    unpublished_events = list(
        filter(
            lambda event: event.mobilizon_id not in unpublished_event_models,
            unpublished_mobilizon_events,
        )
    )

    for event in unpublished_events:
        event_model = await save_event(event)
        for publisher in active_publishers:
            await save_publication(
                publisher, event_model, status=PublicationStatus.WAITING
            )


@atomic(CONNECTION_NAME)
async def save_publication_report(
    coordinator_report: PublisherCoordinatorReport, event: MobilizonEvent
) -> None:
    publications: dict[UUID, Publication] = {
        p.id: p for p in await get_mobilizon_event_publications(event)
    }

    for publication_id, publication_report in coordinator_report:

        publications[publication_id].status = publication_report.status
        publications[publication_id].reason = publication_report.reason
        publications[publication_id].timestamp = arrow.now().datetime

        await publications[publication_id].save()
