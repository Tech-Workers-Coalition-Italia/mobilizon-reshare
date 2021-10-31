import logging
from typing import List, Iterable, Optional
from uuid import UUID

import arrow
from tortoise.transactions import atomic

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication, PublicationStatus
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.coordinator import PublisherCoordinatorReport
from mobilizon_reshare.storage.query import CONNECTION_NAME
from mobilizon_reshare.storage.query.read_query import events_without_publications


@atomic(CONNECTION_NAME)
async def save_publication_report(
    coordinator_report: PublisherCoordinatorReport, publications: List[Publication],
) -> None:
    publications = {m.id: m for m in publications}
    for publication_report in coordinator_report.reports:
        publication_id = publication_report.publication.id
        publications[publication_id].status = publication_report.status
        publications[publication_id].reason = publication_report.reason
        publications[publication_id].timestamp = arrow.now().datetime

        await publications[publication_id].save()


@atomic(CONNECTION_NAME)
async def create_unpublished_events(
    unpublished_mobilizon_events: Iterable[MobilizonEvent],
) -> List[MobilizonEvent]:
    # We store only new events, i.e. events whose mobilizon_id wasn't found in the DB.
    unpublished_event_models: set[UUID] = set(
        map(lambda event: event.mobilizon_id, await events_without_publications())
    )
    unpublished_events = list(
        filter(
            lambda event: event.mobilizon_id not in unpublished_event_models,
            unpublished_mobilizon_events,
        )
    )

    for event in unpublished_events:
        await save_event(event)

    return unpublished_events


@atomic(CONNECTION_NAME)
async def save_publication(
    publisher_name: str, event_model: Event, status: PublicationStatus
) -> Publication:
    publication = await event_model.build_publication_by_publisher_name(
        publisher_name, status
    )
    await publication.save()
    return publication


async def create_publisher(name: str, account_ref: Optional[str] = None) -> None:
    await Publisher.create(name=name, account_ref=account_ref)


@atomic(CONNECTION_NAME)
async def update_publishers(names: Iterable[str],) -> None:
    names = set(names)
    known_publisher_names = set(p.name for p in await Publisher.all())
    for name in names.difference(known_publisher_names):
        logging.info(f"Creating {name} publisher")
        await create_publisher(name)


async def save_event(event: MobilizonEvent) -> Event:
    event_model = event.to_model()
    await event_model.save()
    return event_model
