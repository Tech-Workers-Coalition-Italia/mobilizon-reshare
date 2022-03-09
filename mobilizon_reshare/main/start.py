import logging.config

from mobilizon_reshare.main.publish import publish
from mobilizon_reshare.main.pull import pull

logger = logging.getLogger(__name__)


async def start():
    """
    STUB
    :return:
    """
    events = await pull()
    return await publish(events)
