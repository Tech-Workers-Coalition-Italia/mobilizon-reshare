import asyncio
import atexit
import logging
from pathlib import Path

from tortoise import Tortoise

from mobilizon_bots.config.publishers import publisher_names
from mobilizon_bots.storage.query import create_publisher

logger = logging.getLogger(__name__)


class MobilizonBotsDB:
    def __init__(self, path: Path):
        self.path = path
        # TODO: Check if DB is openable/"queriable"
        self.is_init = self.path.exists() and (not self.path.is_dir())
        if not self.is_init:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    async def setup(self):
        await Tortoise.init(
            db_url=f"sqlite:///{self.path}",
            modules={
                "models": [
                    "mobilizon_bots.models.event",
                    "mobilizon_bots.models.notification",
                    "mobilizon_bots.models.publication",
                    "mobilizon_bots.models.publisher",
                ]
            },
            # always store UTC time in database
            use_tz=True,
        )
        if not self.is_init:
            await Tortoise.generate_schemas()
            for name in publisher_names:
                logging.info(f"Creating {name} publisher")
                # TODO: Deal with account_ref
                await create_publisher(name)
            self.is_init = True
            logger.info(f"Succesfully initialized database at {self.path}")


@atexit.register
def gracefully_tear_down():
    logger.info("Shutting down DB")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(Tortoise.close_connections())
