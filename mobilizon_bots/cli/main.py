import logging.config


from mobilizon_bots.event.event_selection_strategies import select_event_to_publish
from mobilizon_bots.mobilizon.events import get_unpublished_events
from mobilizon_bots.models.publication import PublicationStatus
from mobilizon_bots.publishers import get_active_publishers
from mobilizon_bots.publishers.coordinator import PublisherCoordinator
from mobilizon_bots.storage.query import (
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

    active_publishers = get_active_publishers()

    # Load past events
    published_events = list(await get_published_events())

    # Pull unpublished events from Mobilizon
    unpublished_events = get_unpublished_events(published_events)
    # Store in the DB only the ones we didn't know about
    await create_unpublished_events(unpublished_events, active_publishers)
    event = select_event_to_publish(
        published_events,
        # We must load unpublished events from DB since it contains
        # merged state between Mobilizon and previous WAITING events.
        list(await get_db_unpublished_events()),
    )
    if event:
        logger.debug(f"Event to publish found: {event.name}")
        result = PublisherCoordinator(
            event,
            [
                (pub.id, pub.publisher.name)
                for pub in await publications_with_status(
                    status=PublicationStatus.WAITING,
                    event_mobilizon_id=event.mobilizon_id,
                )
            ],
        ).run()
        await save_publication_report(result, event)

        return 0 if result.successful else 1
    else:
        return 0
