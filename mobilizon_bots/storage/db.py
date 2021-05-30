import asyncio
import atexit
import logging

from pathlib import Path

from tortoise import Tortoise

logger = logging.getLogger(__name__)


class MobilizonBotsDB:
    def __init__(self, path: Path = None):
        self.path = path

    async def setup(self):
        await Tortoise.init(
            db_url=f"sqlite:///{self.path}",
            modules={"models": ["mobilizon_bots.event.model"]},
        )
        if not self.is_init():
            # Generate the schema
            await Tortoise.generate_schemas()

    def is_init(self) -> bool:
        # TODO: Check if DB is openable/"queriable"
        return self.path.exists() and (not self.path.is_dir())


@atexit.register
def gracefully_tear_down():
    logger.info("Shutting down DB")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Tortoise.close_connections())
