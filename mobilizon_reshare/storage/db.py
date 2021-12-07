import logging
import asyncio
from pathlib import Path
from tortoise import Tortoise
from aerich import Command
from mobilizon_reshare.config.publishers import publisher_names
from mobilizon_reshare.storage.query.write import update_publishers

from mobilizon_reshare.config.config import get_settings

logger = logging.getLogger(__name__)


def get_db_url():
    """gets db url from settings

    Returns:
        str : db url
    """
    settings = get_settings()
    db_path = Path(settings.db_path)
    db_url = f"sqlite:///{db_path}"
    return db_url


TORTOISE_ORM = {
    "connections": {"default": get_db_url()},
    "apps": {
        "models": {
            "models": ["mobilizon_reshare.models.event",
                       "mobilizon_reshare.models.notification",
                       "mobilizon_reshare.models.publication",
                       "mobilizon_reshare.models.publisher", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def shutdown(loop):
    """shutdown method"""
    logging.critical("SHUTDOWN CALLED")
    logging.info("closing database connections")
    tasks = [t for t in asyncio.all_tasks() if t is asyncio.current_task()]
    _ = [task.cancel() for task in tasks]
    logging.info("Cancelling %i tasks", len(tasks))
    await asyncio.gather(*tasks, return_exceptions=True)
    logging.info("flushing metrics")
    loop.stop()


async def handle_exception(loop, context):
    """exception handler"""
    logging.critical("HANDLER CALLED")
    msg = context.get("exception", context["message"])
    logging.critical("Caught exception: %s", msg)
    logging.info("shutting down")
    await shutdown(loop)
    await tear_down()


class MoReDB:
    def __init__(self, path: Path):
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(handle_exception)

        self.path = path
        # TODO: Check if DB is openable/"queriable"
        self.is_init = self.path.exists() and (not self.path.is_dir())
        if not self.is_init:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    async def _implement_db_changes(self):
        logging.info("Updating database to latest version")
        try:

            command = Command(tortoise_config=TORTOISE_ORM, app='models',
                              location='./migrations')
            await command.init()
            await command.upgrade()
        except FileNotFoundError:
            logging.critical("aerich configuration not found, fatal error")
            raise

    async def setup(self):
        implement_db_changes = asyncio.create_task(self._implement_db_changes())
        _, _ = await asyncio.wait({implement_db_changes},
                                  return_when=asyncio.FIRST_EXCEPTION)
        if implement_db_changes.exception():
            logging.critical("exception during aerich init")
            raise implement_db_changes.exception()
        await Tortoise.init(
            db_url=get_db_url(),
            modules={
                "models": [
                    "mobilizon_reshare.models.event",
                    "mobilizon_reshare.models.notification",
                    "mobilizon_reshare.models.publication",
                    "mobilizon_reshare.models.publisher",
                ]
            },
            # always store UTC time in database
            use_tz=True,
        )
        if not self.is_init:
            await Tortoise.generate_schemas()
            self.is_init = True
            logger.info(f"Successfully initialized database at {self.path}")

        await update_publishers(publisher_names)


async def tear_down():
    return await Tortoise.close_connections()
