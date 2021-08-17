from uuid import UUID

import pytest

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import PublicationStatus, Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.coordinator import (
    PublisherCoordinatorReport,
    PublicationReport,
    PublisherCoordinator,
)


@pytest.mark.parametrize(
    "statuses, successful",
    [
        [[PublicationStatus.COMPLETED, PublicationStatus.COMPLETED], True],
        [[PublicationStatus.WAITING, PublicationStatus.COMPLETED], False],
        [[PublicationStatus.COMPLETED, PublicationStatus.FAILED], False],
        [[], True],
        [[PublicationStatus.COMPLETED], True],
    ],
)
def test_publication_report_successful(statuses, successful):
    reports = {}
    for i, status in enumerate(statuses):
        reports[UUID(int=i)] = PublicationReport(
            reason=None, publication_id=None, status=status
        )
    assert PublisherCoordinatorReport(None, reports).successful == successful


@pytest.fixture
@pytest.mark.asyncio
async def mock_publication(test_event: MobilizonEvent,):
    event = test_event.to_model()
    await event.save()
    publisher = Publisher(name="telegram")
    await publisher.save()
    publication = Publication(
        id=UUID(int=1),
        status=PublicationStatus.WAITING,
        event=event,
        publisher=publisher,
        timestamp=None,
        reason=None,
    )
    await publication.save()
    return publication


@pytest.mark.asyncio
async def test_coordinator_run_success(
    test_event, mock_publication, mock_publisher_valid
):
    coordinator = PublisherCoordinator(
        test_event, {UUID(int=1): mock_publication, UUID(int=2): mock_publication}
    )
    coordinator.publishers_by_publication_id = {
        UUID(int=1): mock_publisher_valid,
        UUID(int=2): mock_publisher_valid,
    }

    report = coordinator.run()
    assert len(report.reports) == 2
    assert report.successful, "\n".join(
        map(lambda rep: rep.reason, report.reports.values())
    )


@pytest.mark.asyncio
async def test_coordinator_run_failure(
    test_event, mock_publication, mock_publisher_invalid
):
    coordinator = PublisherCoordinator(test_event, {UUID(int=1): mock_publication})
    coordinator.publishers_by_publication_id = {
        UUID(int=1): mock_publisher_invalid,
    }

    report = coordinator.run()
    assert len(report.reports) == 1
    assert not report.successful
    assert (
        list(report.reports.values())[0].reason
        == "Invalid credentials, Invalid event, Invalid message"
    )
