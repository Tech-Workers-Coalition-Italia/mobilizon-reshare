import logging
import click

from mobilizon_reshare.config.command import CommandConfig
from mobilizon_reshare.main.publish import select_and_publish, publish_by_mobilizon_id

logger = logging.getLogger(__name__)


async def publish_command(event_mobilizon_id: click.UUID, platform: str, command_config: CommandConfig):
    """
    Select an event with the current configured strategy
    and publish it to all active platforms.
    """
    if event_mobilizon_id is not None:
        report = await publish_by_mobilizon_id(
            event_mobilizon_id,
            command_config,
            [platform] if platform is not None else None,
        )
    else:
        report = await select_and_publish(command_config)
    return 0 if report and report.successful else 1
