from typing import Iterable, Optional

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import PublicationStatus
from mobilizon_bots.models.publisher import Publisher


async def events_with_status(statuses: list[PublicationStatus]) -> Iterable[MobilizonEvent]:
    return map(
        MobilizonEvent.from_model,
        await Event.filter(
            publications__status__in=statuses
        )
        .prefetch_related("publications")
        .prefetch_related("publications__publisher")
        .order_by("begin_datetime")
        .distinct()
    )


async def get_published_events() -> Iterable[MobilizonEvent]:
    return await events_with_status([
            PublicationStatus.COMPLETED,
            PublicationStatus.PARTIAL,
        ])


async def get_unpublished_events() -> Iterable[MobilizonEvent]:
    return await events_with_status([
            PublicationStatus.WAITING,
        ])


async def create_publisher(name: str, account_ref: Optional[str] = None) -> None:
    await Publisher.create(name=name, account_ref=account_ref)
