import logging.config
from typing import Optional

from mobilizon_reshare.main.publish import publish
from mobilizon_reshare.main.pull import pull
from mobilizon_reshare.publishers.coordinator import PublisherCoordinatorReport

logger = logging.getLogger(__name__)


async def start() -> Optional[PublisherCoordinatorReport]:
    """
    STUB
    :return:
    """
    events = await pull()
    return await publish(events)
