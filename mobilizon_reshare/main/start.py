import logging.config

from mobilizon_reshare.config.command import CommandConfig
from mobilizon_reshare.main.publish import select_and_publish
from mobilizon_reshare.main.pull import pull
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    PublisherCoordinatorReport,
)

logger = logging.getLogger(__name__)


async def start(command_config: CommandConfig) -> PublisherCoordinatorReport:
    """
    STUB
    :return:
    """
    events = await pull()
    return await select_and_publish(command_config, events,)
