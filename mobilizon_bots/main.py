import logging.config
from pathlib import Path

from mobilizon_bots.config.config import update_settings_files
from mobilizon_bots.config.publishers import get_active_publishers
from mobilizon_bots.event.event_selection_strategies import (
    EventSelector,
    SelectNextEventStrategy,
)
from mobilizon_bots.mobilizon.events import get_unpublished_events
from mobilizon_bots.publishers.coordinator import PublisherCoordinator
from mobilizon_bots.storage.db import MobilizonBotsDB
from mobilizon_bots.storage.query import get_published_events, create_unpublished_events
from mobilizon_bots.storage.query import (
    get_unpublished_events as get_db_unpublished_events,
)

logger = logging.getLogger(__name__)


async def main(settings_file):
    """
    STUB
    :return:
    """
    settings = update_settings_files(settings_file)

    logging.config.dictConfig(settings["logging"])
    active_publishers = get_active_publishers(settings)

    db = MobilizonBotsDB(Path(settings.db_path))
    await db.setup()

    # Load past events
    published_events = list(await get_published_events())

    # Pull unpublished events from Mobilizon
    unpublished_events = get_unpublished_events(published_events)
    # Store in the DB only the ones we didn't know about
    await create_unpublished_events(unpublished_events, active_publishers)
    unpublished_events = list(await get_db_unpublished_events())

    event_selector = EventSelector(
        unpublished_events=unpublished_events, published_events=published_events
    )
    strategy = SelectNextEventStrategy()
    event = event_selector.select_event_to_publish(strategy)

    result = PublisherCoordinator(event).run() if event else exit(0)
    exit(0 if result.successful else 1)
