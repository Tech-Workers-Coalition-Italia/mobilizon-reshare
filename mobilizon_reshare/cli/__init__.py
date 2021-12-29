import asyncio
import logging
import traceback
from logging.config import dictConfig
from pathlib import Path

from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.storage.db import tear_down, MoReDB

logger = logging.getLogger(__name__)


async def graceful_exit(code):
    await tear_down()
    exit(code)


async def init():
    settings = get_settings()
    dictConfig(settings["logging"])
    db_path = Path(settings.db_path)
    db = MoReDB(db_path)
    db_setup = asyncio.create_task(db.setup())
    _, _ = await asyncio.wait({db_setup}, return_when=asyncio.FIRST_EXCEPTION)
    if db_setup.exception():
        logging.critical("exception during db setup")
        raise db_setup.exception()


async def _safe_execution(f):
    init_task = asyncio.create_task(init())
    _, _ = await asyncio.wait({init_task}, return_when=asyncio.FIRST_EXCEPTION)
    if init_task.exception():
        logging.critical("exception during init")
        # raise init_task.exception()
        # sys.exit(1)
        loop = asyncio.get_event_loop()
        loop.stop()

    return_code = 1
    try:
        return_code = await f()
    except Exception:
        traceback.print_exc()
    finally:
        logger.debug("Closing")
        await graceful_exit(return_code)


def safe_execution(f):
    asyncio.run(_safe_execution(f))
