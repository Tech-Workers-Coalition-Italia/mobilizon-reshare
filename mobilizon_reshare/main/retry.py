import logging
from typing import Optional
from uuid import UUID

from mobilizon_reshare.publishers.coordinator import (
    PublisherCoordinator,
    PublisherCoordinatorReport,
    PublicationFailureLoggerCoordinator,
)
from mobilizon_reshare.storage.query.exceptions import EventNotFound
from mobilizon_reshare.storage.query.read import (
    get_failed_publications_for_event,
    get_publication,
)
from mobilizon_reshare.storage.query.write import save_publication_report

logger = logging.getLogger(__name__)


async def retry_event_publications(event_id):

    failed_publications = await get_failed_publications_for_event(event_id)
    if not failed_publications:
        logger.info("No failed publications found.")
        return

    logger.info(f"Found {len(failed_publications)} publications.")
    return PublisherCoordinator(failed_publications).run()


async def retry_publication(publication_id) -> Optional[PublisherCoordinatorReport]:
    # TODO test this function
    publication = await get_publication(publication_id)
    if not publication:
        logger.info(f"Publication {publication_id} not found.")
        return

    logger.info(f"Publication {publication_id} found.")
    reports = PublisherCoordinator([publication]).run()

    await save_publication_report(reports)

    for report in reports.reports:
        if not report.succesful:
            PublicationFailureLoggerCoordinator(report,).notify_failure()


async def retry_event(
    mobilizon_event_id: UUID = None,
) -> Optional[PublisherCoordinatorReport]:
    if mobilizon_event_id is None:
        raise NotImplementedError(
            "Autonomous retry not implemented yet, please specify an event_id"
        )
    try:
        reports = await retry_event_publications(mobilizon_event_id)
    except EventNotFound as e:
        logger.debug(e, exc_info=True)
        logger.error(f"Event with id {mobilizon_event_id} not found")
        return

    if not reports:
        return
    await save_publication_report(reports)
    for report in reports.reports:
        if not report.succesful:
            PublicationFailureLoggerCoordinator(report,).notify_failure()
