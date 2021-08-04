import asyncio
import logging
import traceback
from logging.config import dictConfig
from pathlib import Path

from mobilizon_bots.config.config import update_settings_files
from mobilizon_bots.storage.db import tear_down, MobilizonBotsDB

logger = logging.getLogger(__name__)


async def graceful_exit(code):
    await tear_down()
    exit(code)


async def init(settings_file):
    settings = update_settings_files(settings_file)
    dictConfig(settings["logging"])
    db_path = Path(settings.db_path)
    db = MobilizonBotsDB(db_path)
    await db.setup()


async def _safe_execution(f, settings_file):
    await init(settings_file)
    return_code = 1
    try:
        return_code = await f()
    except Exception:
        traceback.print_exc()
    finally:
        logger.debug("Closing")
        await graceful_exit(return_code)


def safe_execution(f, settings_file):
    asyncio.run(_safe_execution(f, settings_file))
