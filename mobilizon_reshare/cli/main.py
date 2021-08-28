import logging.config

from mobilizon_reshare.event.event_selection_strategies import select_event_to_publish
from mobilizon_reshare.mobilizon.events import get_unpublished_events
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers.coordinator import (
    PublicationFailureNotifiersCoordinator,
)
from mobilizon_reshare.publishers.coordinator import PublisherCoordinator
from mobilizon_reshare.storage.query import (
    get_published_events,
    get_unpublished_events as get_db_unpublished_events,
    create_unpublished_events,
    save_publication_report,
    publications_with_status,
)

logger = logging.getLogger(__name__)


async def main():
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
    await create_unpublished_events(unpublished_events)
    event = select_event_to_publish(
        published_events,
        # We must load unpublished events from DB since it contains
        # merged state between Mobilizon and previous WAITING events.
        list(await get_db_unpublished_events()),
    )

    if event:

        waiting_publications = await publications_with_status(
            status=PublicationStatus.WAITING,
            event_mobilizon_id=event.mobilizon_id,
        )
        logger.debug(f"Event to publish found: {event.name}")
        report = PublisherCoordinator(event, waiting_publications).run()
        await save_publication_report(report, waiting_publications)
        PublicationFailureNotifiersCoordinator(event, report).notify_failures()

        return 0 if report.successful else 1
    else:
        return 0
