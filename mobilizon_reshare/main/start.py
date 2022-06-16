import logging.config
from typing import Optional

from config.command import CommandConfig
from mobilizon_reshare.main.publish import select_and_publish
from mobilizon_reshare.main.pull import pull
from mobilizon_reshare.publishers.coordinator import PublisherCoordinatorReport

logger = logging.getLogger(__name__)


async def start(command_config: CommandConfig) -> Optional[PublisherCoordinatorReport]:
    """
    STUB
    :return:
    """
    events = await pull(command_config)
    return await select_and_publish(command_config, events,)
