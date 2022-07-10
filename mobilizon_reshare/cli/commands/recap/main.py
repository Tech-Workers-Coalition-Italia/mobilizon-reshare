import logging.config

from mobilizon_reshare.config.command import CommandConfig
from mobilizon_reshare.main.recap import recap

logger = logging.getLogger(__name__)


async def recap_command(command_config: CommandConfig):

    reports = await recap(command_config)
    return 0 if reports and reports.successful else 1
