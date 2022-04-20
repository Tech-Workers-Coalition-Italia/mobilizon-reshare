import logging.config
from typing import Optional

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.event.event_selection_strategies import select_event_to_publish
from mobilizon_reshare.publishers import get_active_publishers
from mobilizon_reshare.publishers.abstract import EventPublication
from mobilizon_reshare.publishers.coordinator import (
    PublicationFailureNotifiersCoordinator,
    PublisherCoordinatorReport,
)
from mobilizon_reshare.publishers.coordinator import PublisherCoordinator
from mobilizon_reshare.storage.query.read import (
    get_published_events,
    build_publications,
    events_without_publications,
)
from mobilizon_reshare.storage.query.write import save_publication_report

logger = logging.getLogger(__name__)


async def publish_publications(
    publications: list[EventPublication],
) -> PublisherCoordinatorReport:
    report = PublisherCoordinator(publications).run()

    await save_publication_report(report)
    for publication_report in report.reports:
        if not publication_report.succesful:
            PublicationFailureNotifiersCoordinator(
                publication_report,
            ).notify_failure()

    return report


async def publish_event(
    event: MobilizonEvent, publishers: Optional[list[Optional[str]]] = None
) -> PublisherCoordinatorReport:
    logger.info(f"Event to publish found: {event.name}")

    if not (publishers and all(publishers)):
        publishers = get_active_publishers()

    publications = await build_publications(event, publishers)
    return await publish_publications(publications)


async def select_and_publish(
    unpublished_events: Optional[list[MobilizonEvent]] = None,
) -> Optional[PublisherCoordinatorReport]:
    """
    STUB
    :return:
    """
    if unpublished_events is None:
        unpublished_events = await events_without_publications()

    event = select_event_to_publish(
        list(await get_published_events()),
        unpublished_events,
    )

    if event:
        return await publish_event(event)
    else:
        logger.info("No event to publish found")
