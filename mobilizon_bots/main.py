import logging.config
from pathlib import Path

from tortoise import run_async

from mobilizon_bots.config.config import settings
from mobilizon_bots.storage.db import MobilizonBotsDB
from mobilizon_bots.storage.query import get_published_events

logger = logging.getLogger(__name__)


async def main():
    """
    STUB
    :return:
    """
    logging.config.dictConfig(settings.logging)
    db = MobilizonBotsDB(Path(settings.db_path))
    await db.setup()
    published_events = get_published_events()
    unpublished_events = get_unpublished_events(published_events)
    event = select_event_to_publish()
    result = PublisherCoordinator(event).publish() if event else exit(0)
    exit(0 if result.is_success() else 1)


if __name__ == "__main__":
    run_async(main())
