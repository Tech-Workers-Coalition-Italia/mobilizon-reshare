import logging
from typing import Iterable, Optional

import arrow
from tortoise.transactions import atomic

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.coordinator import PublisherCoordinatorReport
from mobilizon_reshare.storage.query import CONNECTION_NAME
from mobilizon_reshare.storage.query.converter import event_to_model
from mobilizon_reshare.storage.query.read import (
    events_without_publications,
    is_known,
    get_publisher_by_name,
    get_event,
)


async def create_publisher(name: str, account_ref: Optional[str] = None) -> None:
    await Publisher.create(name=name, account_ref=account_ref)


@atomic(CONNECTION_NAME)
async def upsert_publication(publication_report, event):

    publisher = await get_publisher_by_name(
        name=publication_report.publication.publisher.name
    )
    old_publication = await Publication.filter(
        id=publication_report.publication.id
    ).first()
    if old_publication:
        # I update the existing publication with the new report
        old_publication.timestamp = arrow.now().datetime
        old_publication.status = publication_report.status
        old_publication.reason = publication_report.reason

        await old_publication.save(force_update=True)
    else:
        # I create a new publication
        await Publication.create(
            id=publication_report.publication.id,
            event_id=event.id,
            publisher_id=publisher.id,
            status=publication_report.status,
            reason=publication_report.reason,
            timestamp=arrow.now().datetime,
        )


@atomic(CONNECTION_NAME)
async def save_publication_report(
    coordinator_report: PublisherCoordinatorReport,
) -> None:
    """
    Store a publication process outcome
    """
    for publication_report in coordinator_report.reports:
        event = await Event.filter(
            mobilizon_id=publication_report.publication.event.mobilizon_id
        ).first()
        await upsert_publication(publication_report, event)


@atomic(CONNECTION_NAME)
async def create_unpublished_events(
    events_from_mobilizon: Iterable[MobilizonEvent],
) -> list[MobilizonEvent]:
    """
    Computes the difference between remote and local events and store it.

    Returns the unpublished events merged state.
    """
    # There are three cases:
    for event in events_from_mobilizon:
        if not await is_known(event):
            # Either an event is unknown
            await event_to_model(event).save()
        else:
            # Or it's known and changed
            event_model = await get_event(event.mobilizon_id)
            if event.last_update_time > event_model.last_update_time:
                await event_to_model(event=event, db_id=event_model.id).save(
                    force_update=True
                )
            # Or it's known and unchanged, in which case we do nothing.

    return await events_without_publications()


@atomic(CONNECTION_NAME)
async def update_publishers(names: Iterable[str],) -> None:
    names = set(names)
    known_publisher_names = set(p.name for p in await Publisher.all())
    for name in names.difference(known_publisher_names):
        logging.info(f"Creating {name} publisher")
        await create_publisher(name)
