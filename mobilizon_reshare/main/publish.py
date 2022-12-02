import logging.config
from typing import Optional, Iterator

from mobilizon_reshare.config.command import CommandConfig
from mobilizon_reshare.dataclasses import MobilizonEvent
from mobilizon_reshare.dataclasses.event import (
    get_published_events,
    get_mobilizon_events_without_publications,
)
from mobilizon_reshare.dataclasses.publication import (
    _EventPublication,
    build_publications_for_event,
)
from mobilizon_reshare.event.event_selection_strategies import select_event_to_publish
from mobilizon_reshare.publishers import get_active_publishers
from mobilizon_reshare.publishers.coordinators.event_publishing.dry_run import (
    DryRunPublisherCoordinator,
)
from mobilizon_reshare.publishers.coordinators.event_publishing.notify import (
    PublicationFailureNotifiersCoordinator,
)
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    PublisherCoordinatorReport,
    PublisherCoordinator,
)
from mobilizon_reshare.storage.query.write import (
    save_publication_report,
    save_notification_report,
)

logger = logging.getLogger(__name__)


async def publish_publications(
    publications: list[_EventPublication],
) -> PublisherCoordinatorReport:
    publishers_report = PublisherCoordinator(publications).run()
    await save_publication_report(publishers_report)

    for publication_report in publishers_report.reports:
        if not publication_report.successful:
            notifiers_report = PublicationFailureNotifiersCoordinator(publication_report,).notify_failure()
            if notifiers_report:
                await save_notification_report(notifiers_report)

    return publishers_report


def perform_dry_run(publications: list[_EventPublication]):
    return DryRunPublisherCoordinator(publications).run()


async def publish_event(
    event: MobilizonEvent,
    command_config: CommandConfig,
    publishers: Optional[Iterator[str]] = None,
) -> PublisherCoordinatorReport:
    logger.info(f"Event to publish found: {event.name}")

    if not (publishers and all(publishers)):
        publishers = get_active_publishers()

    publications = await build_publications_for_event(event, publishers)
    if command_config.dry_run:
        logger.info("Executing in dry run mode. No event is going to be published.")
        return perform_dry_run(publications)
    else:
        return await publish_publications(publications)


async def select_and_publish(
    command_config: CommandConfig,
    unpublished_events: Optional[list[MobilizonEvent]] = None,
) -> Optional[PublisherCoordinatorReport]:
    """
    STUB
    :return:
    """
    if unpublished_events is None:
        unpublished_events = await get_mobilizon_events_without_publications()

    event = select_event_to_publish(
        list(await get_published_events()), unpublished_events,
    )

    if event:
        return await publish_event(event, command_config)
    else:
        logger.info("No event to publish found")
