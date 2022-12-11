import logging
from typing import Optional
from uuid import UUID

from tortoise.exceptions import DoesNotExist

from mobilizon_reshare.dataclasses import MobilizonEvent, EventPublication
from mobilizon_reshare.dataclasses.publication import get_failed_publications_for_event
from mobilizon_reshare.main.publish import publish_publications
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    PublisherCoordinatorReport,
)
from mobilizon_reshare.storage.query.exceptions import EventNotFound

logger = logging.getLogger(__name__)


async def retry_event_publications(event_id) -> Optional[PublisherCoordinatorReport]:
    event = await MobilizonEvent.retrieve(event_id)
    failed_publications = await get_failed_publications_for_event(event)
    if not failed_publications:
        logger.info("No failed publications found.")
        return

    logger.info(f"Found {len(failed_publications)} publications.")
    return await publish_publications(failed_publications)


async def retry_publication(publication_id) -> Optional[PublisherCoordinatorReport]:
    try:
        publication = await EventPublication.retrieve(publication_id)
    except DoesNotExist:
        logger.info(f"Publication {publication_id} not found.")
        return

    logger.info(f"Publication {publication_id} found.")
    return await publish_publications([publication])


async def retry_event(
    mobilizon_event_id: UUID = None,
) -> Optional[PublisherCoordinatorReport]:
    if mobilizon_event_id is None:
        raise NotImplementedError(
            "Autonomous retry not implemented yet, please specify an event_id"
        )
    try:
        return await retry_event_publications(mobilizon_event_id)
    except EventNotFound as e:
        logger.debug(e, exc_info=True)
        logger.error(f"Event with id {mobilizon_event_id} not found")
        return
