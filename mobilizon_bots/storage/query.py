from typing import Iterable, Optional

from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publisher import Publisher


async def get_published_events() -> Iterable[MobilizonEvent]:
    return map(
        MobilizonEvent.from_model,
        await Event.filter(
            publications__status__in=[
                PublicationStatus.COMPLETED,
                PublicationStatus.PARTIAL,
            ]
        )
        .order_by("begin_datetime")
        .distinct(),
    )


async def create_publisher(name: str, account_ref: Optional[str] = None):
    await Publisher.create(name=name, account_ref=account_ref)
