import logging.config
from pathlib import Path

from more.config.config import update_settings_files
from more.config.publishers import get_active_publishers
from more.event.event_selection_strategies import select_event_to_publish
from more.mobilizon.events import get_unpublished_events
from more.publishers.coordinator import PublisherCoordinator
from more.storage.db import MoreDB
from more.storage.query import get_published_events, create_unpublished_events

logger = logging.getLogger(__name__)


async def main(settings_file):
    """
    STUB
    :return:
    """
    settings = update_settings_files(settings_file)

    logging.config.dictConfig(settings["logging"])
    active_publishers = get_active_publishers(settings)

    db = MoreDB(Path(settings.db_path))
    await db.setup()

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
        exit(0 if result.successful else 1)
    else:
        logger.debug("Closing")
        exit(0)
