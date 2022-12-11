import logging
from typing import Optional, List

from arrow import now

from mobilizon_reshare.config.command import CommandConfig
from mobilizon_reshare.dataclasses import EventPublicationStatus
from mobilizon_reshare.dataclasses import MobilizonEvent
from mobilizon_reshare.dataclasses.event import get_mobilizon_events_with_status
from mobilizon_reshare.dataclasses.publication import RecapPublication
from mobilizon_reshare.publishers import get_active_publishers
from mobilizon_reshare.publishers.coordinators import BaseCoordinatorReport
from mobilizon_reshare.publishers.coordinators.event_publishing.notify import (
    PublicationFailureNotifiersCoordinator,
)
from mobilizon_reshare.publishers.coordinators.recap_publishing.dry_run import (
    DryRunRecapCoordinator,
)
from mobilizon_reshare.publishers.coordinators.recap_publishing.recap import (
    RecapCoordinator,
)
from mobilizon_reshare.publishers.platforms.platform_mapping import (
    get_publisher_class,
    get_formatter_class,
)

logger = logging.getLogger(__name__)


async def select_events_to_recap() -> List[MobilizonEvent]:
    return list(
        await get_mobilizon_events_with_status(
            status=[EventPublicationStatus.COMPLETED], from_date=now()
        )
    )


async def recap(command_config: CommandConfig) -> Optional[BaseCoordinatorReport]:
    # I want to recap only the events that have been successfully published and that haven't happened yet
    events_to_recap = await select_events_to_recap()

    if events_to_recap:
        logger.info(f"Found {len(events_to_recap)} events to recap.")
        recap_publications = [
            RecapPublication(
                get_publisher_class(publisher)(),
                get_formatter_class(publisher)(),
                events_to_recap,
            )
            for publisher in get_active_publishers()
        ]
        if command_config.dry_run:
            reports = DryRunRecapCoordinator(recap_publications).run()
        else:
            reports = RecapCoordinator(recap_publications).run()

        for report in reports.reports:
            if report.status == EventPublicationStatus.FAILED:
                PublicationFailureNotifiersCoordinator(report).notify_failure()
        return reports
    else:
        logger.info("Found no events")
