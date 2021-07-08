from typing import Iterable, Optional

from tortoise.transactions import atomic

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import Publication, PublicationStatus
from mobilizon_bots.models.publisher import Publisher


async def events_with_status(
    statuses: list[PublicationStatus],
) -> Iterable[MobilizonEvent]:
    return map(
        MobilizonEvent.from_model,
        await Event.filter(publications__status__in=statuses)
        .prefetch_related("publications")
        .prefetch_related("publications__publisher")
        .order_by("begin_datetime")
        .distinct(),
    )


async def get_published_events() -> Iterable[MobilizonEvent]:
    return await events_with_status(
        [PublicationStatus.COMPLETED, PublicationStatus.PARTIAL]
    )


async def get_unpublished_events() -> Iterable[MobilizonEvent]:
    return await events_with_status([PublicationStatus.WAITING])


@atomic("models")
async def save_events(unpublished_events, active_publishers):

    for event in unpublished_events:
        event_model = event.to_model()
        await event_model.save()

        for publisher_name in active_publishers:
            publisher = await Publisher.filter(name=publisher_name).first()
            await Publication.create(
                status=PublicationStatus.WAITING,
                event_id=event_model.id,
                publisher_id=publisher.id,
            )


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

    if unpublished_events:
        await save_events(unpublished_events, active_publishers)


async def create_publisher(name: str, account_ref: Optional[str] = None) -> None:
    await Publisher.create(name=name, account_ref=account_ref)
