import logging

from mobilizon_reshare.main.publish import (
    select_and_publish,
    publish_event,
    publish_publications,
)
from mobilizon_reshare.storage.query.read import get_mobilizon_event, get_publication

logger = logging.getLogger(__name__)


async def publish_command(event, publication, platform):
    """
    If no arguments are provided, select an event with the current configured strategy
    and publish it to all active platforms.

    - If list_platforms is True print all platforms and exit
    - Otherwise:
       + If publication is not None, publish it.
       + Otherwise if event is not None publish it.
    """
    if publication and event:
        logger.error("-P/--publication and -E/--event are incompatible!")
        return 1

    if publication:
        report = await publish_publications(await get_publication(publication))
    elif event:
        report = await publish_event(await get_mobilizon_event(event), [platform])
    else:
        report = await select_and_publish()
    return 0 if report and report.successful else 1
