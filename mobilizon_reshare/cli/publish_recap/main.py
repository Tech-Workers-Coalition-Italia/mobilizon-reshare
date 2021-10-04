import logging.config
from typing import List

from arrow import now

from mobilizon_reshare.event.event import EventPublicationStatus, MobilizonEvent
from mobilizon_reshare.publishers import get_active_publishers
from mobilizon_reshare.publishers.abstract import RecapPublication
from mobilizon_reshare.publishers.coordinator import RecapCoordinator
from mobilizon_reshare.publishers.platforms.platform_mapping import (
    get_publisher_class,
    get_formatter_class,
)
from mobilizon_reshare.storage.query import events_with_status

logger = logging.getLogger(__name__)


async def select_events_to_recap() -> List[MobilizonEvent]:
    return list(
        await events_with_status(
            status=[EventPublicationStatus.COMPLETED], from_date=now()
        )
    )


async def main():
    # I want to recap only the events that have been succesfully published and that haven't happened yet
    events_to_recap = await select_events_to_recap()
    if events_to_recap:
        recap_publications = [
            RecapPublication(
                get_publisher_class(publisher)(),
                get_formatter_class(publisher)(),
                events_to_recap,
            )
            for publisher in get_active_publishers()
        ]
        RecapCoordinator(recap_publications).run()
        return 0
    else:
        return 0
