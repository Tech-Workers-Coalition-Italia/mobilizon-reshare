import logging.config

from mobilizon_reshare.event.event_selection_strategies import select_event_to_publish
from mobilizon_reshare.mobilizon.events import get_mobilizon_future_events
from mobilizon_reshare.publishers.coordinator import (
    PublicationFailureNotifiersCoordinator,
)
from mobilizon_reshare.publishers.coordinator import PublisherCoordinator
from mobilizon_reshare.storage.query.read import (
    get_published_events,
    build_publications,
)
from mobilizon_reshare.storage.query.write import (
    create_unpublished_events,
    save_publication_report,
)

logger = logging.getLogger(__name__)


async def start():
    """
    STUB
    :return:
    """

    # Pull future events from Mobilizon
    future_events = get_mobilizon_future_events()
    # Store in the DB only the ones we didn't know about
    events_without_publications = await create_unpublished_events(future_events)
    event = select_event_to_publish(
        list(await get_published_events()),
        # We must load unpublished events from DB since it contains
        # merged state between Mobilizon and previous WAITING events.
        events_without_publications,
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
    else:
        logger.info("No event to publish found")
