import logging.config

from mobilizon_reshare.event.event_selection_strategies import select_event_to_publish
from mobilizon_reshare.mobilizon.events import get_unpublished_events
from mobilizon_reshare.publishers import get_active_publishers
from mobilizon_reshare.publishers.coordinator import (
    PublicationFailureNotifiersCoordinator,
)
from mobilizon_reshare.publishers.coordinator import PublisherCoordinator
from mobilizon_reshare.storage.query import (
    get_published_events,
    create_unpublished_events,
    save_publication_report,
    create_publications_for_publishers,
)

logger = logging.getLogger(__name__)


async def main():
    """
    STUB
    :return:
    """
    active_publishers = get_active_publishers()

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
        logger.debug(f"Event to publish found: {event.name}")

        publications, models = await create_publications_for_publishers(
            event, active_publishers
        )
        reports = PublisherCoordinator(publications).run()

        await save_publication_report(reports, models)
        for report in reports.reports:
            PublicationFailureNotifiersCoordinator(report).notify_failure()
