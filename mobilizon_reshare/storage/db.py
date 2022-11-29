import logging
from logging.config import dictConfig
from pathlib import Path

import pkg_resources
import urllib3.util
from aerich import Command
from tortoise import Tortoise

from mobilizon_reshare.config.config import (
    get_settings,
    get_settings_without_validation,
)
from mobilizon_reshare.config.publishers import publisher_names
from mobilizon_reshare.storage.query.write import update_publishers

logger = logging.getLogger(__name__)


def get_db_url() -> urllib3.util.Url:
    return urllib3.util.parse_url(get_settings_without_validation().db_url)


def get_tortoise_orm():

    return {
        "connections": {"default": get_db_url().url},
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
    def get_migration_location(self):
        scheme = get_db_url().scheme
        return pkg_resources.resource_filename(
            "mobilizon_reshare", f"migrations/{scheme}"
        )

    async def _implement_db_changes(self):
        logging.info("Performing aerich migrations.")
        command = Command(
            tortoise_config=get_tortoise_orm(),
            app="models",
            location=self.get_migration_location(),
        )
        await command.init()
        migrations = await command.upgrade()
        if migrations:
            logging.info("Updated database to latest version")

    async def setup(self):
        tortoise_config = get_tortoise_orm()
        Tortoise.init_models(
            tortoise_config["apps"]["models"]["models"], "models", _init_relations=True
        )
        await self._implement_db_changes()
        await Tortoise.init(config=tortoise_config)
        await Tortoise.generate_schemas()
        await update_publishers(publisher_names)


class MoReSQLiteDB(MoReDB):
    def __init__(self):

        if (
            get_db_url().path
        ):  # if in-memory sqlite there's no path so nothing has to be initialized
            self.path = Path(get_db_url().path)
            # TODO: Check if DB is openable/"queriable"
            self.is_init = self.path.exists() and (not self.path.is_dir())
            if not self.is_init:
                self.path.parent.mkdir(parents=True, exist_ok=True)


async def tear_down():
    return await Tortoise.close_connections()


async def init(init_logging=True):

    if init_logging:
        dictConfig(get_settings()["logging"])

    # init storage
    url = get_db_url()
    if url.scheme == "sqlite":
        db = MoReSQLiteDB()
    else:
        db = MoReDB()
    await db.setup()
