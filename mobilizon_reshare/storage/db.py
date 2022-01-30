import logging
from pathlib import Path

import pkg_resources
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


def get_tortoise_orm():
    return {
        "connections": {"default": get_db_url()},
        "apps": {
            "models": {
                "models": [
                    "mobilizon_reshare.models.event",
                    "mobilizon_reshare.models.notification",
                    "mobilizon_reshare.models.publication",
                    "mobilizon_reshare.models.publisher",
                    "aerich.models",
                ],
                "default_connection": "default",
            },
        },
        # always store UTC time in database
        "use_tz": True,
    }


TORTOISE_ORM = get_tortoise_orm()


class MoReDB:
    def __init__(self, path: Path):
        self.path = path
        # TODO: Check if DB is openable/"queriable"
        self.is_init = self.path.exists() and (not self.path.is_dir())
        if not self.is_init:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    async def _implement_db_changes(self):
        migration_queries_location = pkg_resources.resource_filename(
            "mobilizon_reshare", "migrations"
        )
        command = Command(
            tortoise_config=TORTOISE_ORM,
            app="models",
            location=migration_queries_location,
        )
        await command.init()
        migrations = await command.upgrade()
        if migrations:
            logging.warning("Updated database to latest version")

    async def setup(self):
        await self._implement_db_changes()
        await Tortoise.init(
            config=TORTOISE_ORM,
        )
        if not self.is_init:
            await Tortoise.generate_schemas()
            self.is_init = True
            logger.info(f"Successfully initialized database at {self.path}")

        await update_publishers(publisher_names)


async def tear_down():
    return await Tortoise.close_connections()
