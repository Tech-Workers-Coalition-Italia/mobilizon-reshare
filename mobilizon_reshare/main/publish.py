import logging.config
from typing import Optional

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.event.event_selection_strategies import select_event_to_publish
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


async def publish(
    events: Optional[list[MobilizonEvent]] = None,
) -> Optional[PublisherCoordinatorReport]:
    """
    STUB
    :return:
    """
    if events is None:
        events = await events_without_publications()

    event = select_event_to_publish(
        list(await get_published_events()),
        events,
    )

    if event:
        logger.info(f"Event to publish found: {event.name}")

        publications = await build_publications(event)
        reports = PublisherCoordinator(publications).run()

        await save_publication_report(reports)
        for report in reports.reports:
            if not report.succesful:
                PublicationFailureNotifiersCoordinator(
                    report,
                ).notify_failure()
        return reports
    else:
        logger.info("No event to publish found")
