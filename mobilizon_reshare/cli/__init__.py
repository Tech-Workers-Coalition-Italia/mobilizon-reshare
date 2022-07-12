import asyncio
import functools
import logging
import traceback
from logging.config import dictConfig
from pathlib import Path
import sys

from mobilizon_reshare.config.command import CommandConfig
from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.storage.db import tear_down, MoReDB

logger = logging.getLogger(__name__)


async def graceful_exit():
    await tear_down()


async def init():
    settings = get_settings()
    dictConfig(settings["logging"])
    db_path = Path(settings.db_path)
    db = MoReDB(db_path)
    await db.setup()


async def _safe_execution(function):
    await init()

    return_code = 1
    try:
        return_code = await function()
    except Exception:
        traceback.print_exc()
    finally:
        logger.debug("Closing")
        await graceful_exit()
        return return_code


def safe_execution(function, command_config: CommandConfig = None):
    if command_config:
        function = functools.partial(function, command_config)

    code = asyncio.run(_safe_execution(function))
    sys.exit(code)
