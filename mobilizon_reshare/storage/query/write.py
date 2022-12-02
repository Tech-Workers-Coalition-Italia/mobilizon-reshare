import logging
from typing import Iterable

import arrow
from tortoise.transactions import atomic

from mobilizon_reshare.dataclasses import MobilizonEvent
from mobilizon_reshare.dataclasses.event import (
    get_mobilizon_events_without_publications,
)
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.notification import Notification
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.coordinators.event_publishing import (
    EventPublicationReport,
)
from mobilizon_reshare.publishers.coordinators.event_publishing.notify import (
    NotifierCoordinatorReport,
)
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    PublisherCoordinatorReport,
)
from mobilizon_reshare.storage.query.read import get_event


@atomic()
async def upsert_publication(
    publication_report: EventPublicationReport, event: Event
):

    publisher_model = await (
        Publisher.get(name=publication_report.publication.publisher.name).first()
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
            publisher_id=publisher_model.id,
            status=publication_report.status,
            reason=publication_report.reason,
            timestamp=arrow.now().datetime,
        )


@atomic()
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


@atomic()
async def save_notification_report(
    coordinator_report: NotifierCoordinatorReport,
) -> None:
    """
    Store a notification process outcome
    """
    for report in coordinator_report.reports:
        publisher = await Publisher.filter(name=report.notification.publisher.name).first()

        await Notification.create(
            publication_id=report.notification.publication.id,
            target_id=publisher.id,
            status=report.status,
            message=report.reason,
        )


@atomic()
async def create_unpublished_events(
    events_from_mobilizon: Iterable[MobilizonEvent],
) -> list[MobilizonEvent]:
    """
    Computes the difference between remote and local events and store it.

    Returns the unpublished events merged state.
    """
    # There are three cases:
    for event in events_from_mobilizon:
        if not await Event.exists(mobilizon_id=event.mobilizon_id):
            # Either an event is unknown
            await event.to_model().save()
        else:
            # Or it's known and changed
            event_model = await get_event(event.mobilizon_id)
            if event.last_update_time > event_model.last_update_time:
                await event.to_model(db_id=event_model.id).save(force_update=True)
            # Or it's known and unchanged, in which case we do nothing.

    return await get_mobilizon_events_without_publications()


@atomic()
async def update_publishers(names: Iterable[str],) -> None:
    names = set(names)
    known_publisher_names = set(p.name for p in await Publisher.all())
    for name in names.difference(known_publisher_names):
        logging.info(f"Creating {name} publisher")
        await Publisher.create(name=name, account_ref=None)
