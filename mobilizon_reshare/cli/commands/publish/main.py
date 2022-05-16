import logging

from mobilizon_reshare.main.publish import select_and_publish

logger = logging.getLogger(__name__)


async def publish_command():
    """
    Select an event with the current configured strategy
    and publish it to all active platforms.
    """
    report = await select_and_publish()
    return 0 if report and report.successful else 1
