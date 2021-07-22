import logging.config

from mobilizon_bots.event.event_selection_strategies import select_event_to_publish
from mobilizon_bots.mobilizon.events import get_unpublished_events
from mobilizon_bots.publishers import get_active_publishers
from mobilizon_bots.publishers.coordinator import PublisherCoordinator
from mobilizon_bots.storage.db import tear_down
from mobilizon_bots.storage.query import get_published_events, create_unpublished_events

logger = logging.getLogger(__name__)


async def graceful_exit(code):
    await tear_down()
    exit(code)


async def main():
    """
    STUB
    :return:
    """

    active_publishers = get_active_publishers()

    # Load past events
    published_events = list(await get_published_events())

    # Pull unpublished events from Mobilizon
    unpublished_events = get_unpublished_events(published_events)
    # Store in the DB only the ones we didn't know about
    await create_unpublished_events(unpublished_events, active_publishers)
    event = select_event_to_publish(published_events, unpublished_events)
    if event:
        logger.debug(f"Event to publish found: {event.name}")
        result = PublisherCoordinator(event).run()

        logger.debug("Closing")

        await graceful_exit(0 if result.successful else 1)
    else:
        logger.debug("Closing")
        await graceful_exit(0)
