import logging.config

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.mobilizon.events import get_mobilizon_future_events

from mobilizon_reshare.storage.query.write import (
    create_unpublished_events,
)

logger = logging.getLogger(__name__)


async def pull() -> list[MobilizonEvent]:
    """
    Fetches the latest events from Mobilizon and stores them.
    :return:
    """

    # Pull future events from Mobilizon
    future_events = get_mobilizon_future_events()
    logger.info(f"Pulled {len(future_events)} events from Mobilizon.")
    # Store in the DB only the ones we didn't know about
    events = await create_unpublished_events(future_events)
    logger.debug(f"There are now {len(events)} unpublished events.")
    return events
