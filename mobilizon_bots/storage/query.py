import sys

from typing import Iterable, Optional

from tortoise.queryset import QuerySet
from tortoise.transactions import atomic

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import Publication, PublicationStatus
from mobilizon_bots.models.publisher import Publisher
from mobilizon_bots.publishers.coordinator import PublisherCoordinatorReport

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


async def events_with_status(
    statuses: list[PublicationStatus],
) -> Iterable[MobilizonEvent]:
    return map(
        MobilizonEvent.from_model,
        await prefetch_event_relations(Event.filter(publications__status__in=statuses)),
    )


async def get_published_events() -> Iterable[MobilizonEvent]:
    return map(
        MobilizonEvent.from_model,
        await prefetch_event_relations(
            Event.filter(publications__status=PublicationStatus.COMPLETED)
        ),
    )


async def get_unpublished_events() -> Iterable[MobilizonEvent]:
    return await events_with_status([PublicationStatus.WAITING])


async def save_event(event):

    event_model = event.to_model()
    await event_model.save()
    return event_model


async def save_publication(publisher_name, event_model, status: PublicationStatus):

    publisher = await Publisher.filter(name=publisher_name).first()
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


async def create_publisher(name: str, account_ref: Optional[str] = None) -> None:
    await Publisher.create(name=name, account_ref=account_ref)


async def save_publication_report(publication_report: PublisherCoordinatorReport):
    for publisher_report in publication_report:
        pass
