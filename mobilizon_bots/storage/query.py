from typing import Iterable

from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus
from mobilizon_bots.models.event import Event


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
