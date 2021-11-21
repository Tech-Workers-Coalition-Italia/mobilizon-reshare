import logging
from typing import List, Iterable, Optional

import arrow
from tortoise.transactions import atomic

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.coordinator import PublisherCoordinatorReport
from mobilizon_reshare.storage.query import CONNECTION_NAME
from mobilizon_reshare.storage.query.read import events_without_publications


@atomic(CONNECTION_NAME)
async def save_publication_report(
    coordinator_report: PublisherCoordinatorReport,
    publication_models: List[Publication],
) -> None:
    publication_models = {m.id: m for m in publication_models}
    for publication_report in coordinator_report.reports:
        publication_id = publication_report.publication.id
        publication_models[publication_id].status = publication_report.status
        publication_models[publication_id].reason = publication_report.reason
        publication_models[publication_id].timestamp = arrow.now().datetime

        await publication_models[publication_id].save()


@atomic(CONNECTION_NAME)
async def create_unpublished_events(
    events_from_mobilizon: Iterable[MobilizonEvent],
) -> list[MobilizonEvent]:
    # We store only new events, i.e. events whose mobilizon_id wasn't found in the DB.
    unknown_event_mobilizon_ids = set(
        map(lambda event: event.mobilizon_id, await events_without_publications())
    )
    new_unpublished_events = list(
        filter(
            lambda event: event.mobilizon_id not in unknown_event_mobilizon_ids,
            events_from_mobilizon,
        )
    )

    for event in new_unpublished_events:
        await event.to_model().save()

    return new_unpublished_events


async def create_publisher(name: str, account_ref: Optional[str] = None) -> None:
    await Publisher.create(name=name, account_ref=account_ref)


@atomic(CONNECTION_NAME)
async def update_publishers(names: Iterable[str],) -> None:
    names = set(names)
    known_publisher_names = set(p.name for p in await Publisher.all())
    for name in names.difference(known_publisher_names):
        logging.info(f"Creating {name} publisher")
        await create_publisher(name)