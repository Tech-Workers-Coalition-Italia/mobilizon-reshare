import logging.config
from pathlib import Path

from tortoise import run_async

from mobilizon_bots.config.config import settings

from mobilizon_bots.config.publishers import get_active_publishers
from mobilizon_bots.event.event_selector import EventSelector, SelectNextEventStrategy
from mobilizon_bots.mobilizon.events import get_unpublished_events
from mobilizon_bots.storage.db import MobilizonBotsDB
from mobilizon_bots.storage.query import get_published_events, create_unpublished_events
from mobilizon_bots.storage.query import (
    get_unpublished_events as get_db_unpublished_events,
)

logger = logging.getLogger(__name__)


async def main():
    """
    STUB
    :return:
    """
    logging.config.dictConfig(settings.logging)
    active_publishers = get_active_publishers(settings)

    db = MobilizonBotsDB(Path(settings.db_path))
    await db.setup()

    # Load past events
    published_events = list(await get_published_events())

    # Pull unpublished events from Mobilizon
    unpublished_events = get_unpublished_events(published_events)
    # Store in the DB only the ones we din't know about
    await create_unpublished_events(unpublished_events, active_publishers)
    unpublished_events = list(await get_db_unpublished_events())

    event_selector = EventSelector(
        unpublished_events=unpublished_events, published_events=published_events
    )
    # TODO: Here we should somehow handle publishers
    strategy = SelectNextEventStrategy(minimum_break_between_events_in_minutes=360)
    event = event_selector.select_event_to_publish(strategy)

    result = PublisherCoordinator(event).publish() if event else exit(0)
    exit(0 if result.is_success() else 1)


if __name__ == "__main__":
    run_async(main())
