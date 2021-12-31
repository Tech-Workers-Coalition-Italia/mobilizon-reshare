import logging
from typing import Iterable, Optional

import arrow
from tortoise.transactions import atomic

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication, PublicationStatus
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.coordinator import PublisherCoordinatorReport
from mobilizon_reshare.storage.query import CONNECTION_NAME
from mobilizon_reshare.storage.query.read import events_without_publications


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
    Compute the difference between remote and local events and store it.

    Returns the unpublished events merged state.
    """
    # We store only new events, i.e. events whose mobilizon_id wasn't found in the DB.
    unpublished_events = await events_without_publications()

    # save in known_event_mobilizon_key only unique tuple composed by id and updatedAt from unpublished_events
    known_event_mobilizon_keys = set()
    for event in unpublished_events:
        id_tuple = (event.mobilizon_id, event.last_update_time)
        known_event_mobilizon_keys.add(id_tuple)

    # get list of mobilizon_id publicated successfully
    publications_ok = await Publication.filter(
        status=PublicationStatus.COMPLETED
    ).values_list("id", flat=True)

    # generate list of event to save (insert, update) :
    #
    # - event must not be in known keys
    # - event must not be already successful published
    new_unpublished_events = []
    for event in events_from_mobilizon:
        if (
            event.mobilizon_id not in publications_ok
            and (event.mobilizon_id, event.last_update_time)
            not in known_event_mobilizon_keys
        ):
            new_unpublished_events.append(event)

    for event in new_unpublished_events:
        await event.to_model().save()

    return await events_without_publications()


async def create_publisher(name: str, account_ref: Optional[str] = None) -> None:
    await Publisher.create(name=name, account_ref=account_ref)


@atomic(CONNECTION_NAME)
async def update_publishers(names: Iterable[str],) -> None:
    names = set(names)
    known_publisher_names = set(p.name for p in await Publisher.all())
    for name in names.difference(known_publisher_names):
        logging.info(f"Creating {name} publisher")
        await create_publisher(name)


async def get_publisher_by_name(name):
    return await Publisher.filter(name=name).first()
