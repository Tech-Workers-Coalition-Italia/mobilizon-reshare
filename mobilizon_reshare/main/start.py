import logging.config

from mobilizon_reshare.event.event_selection_strategies import select_event_to_publish
from mobilizon_reshare.mobilizon.events import get_unpublished_events
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

    # TODO: the logic to get published and unpublished events is probably redundant.
    # We need a simpler way to bring together events from mobilizon, unpublished events from the db
    # and published events from the DB

    # Load past events
    published_events = list(await get_published_events())

    # Pull unpublished events from Mobilizon
    unpublished_events = get_unpublished_events(published_events)
    # Store in the DB only the ones we didn't know about
    db_unpublished_events = await create_unpublished_events(unpublished_events)
    event = select_event_to_publish(
        published_events,
        # We must load unpublished events from DB since it contains
        # merged state between Mobilizon and previous WAITING events.
        db_unpublished_events,
    )

    if event:
        logger.info(f"Event to publish found: {event.name}")

        publications = await build_publications(event)
        reports = PublisherCoordinator(publications).run()

        await save_publication_report(reports)
        for report in reports.reports:
            if not report.succesful:
                PublicationFailureNotifiersCoordinator(report,).notify_failure()
    else:
        logger.info("No event to publish found")
