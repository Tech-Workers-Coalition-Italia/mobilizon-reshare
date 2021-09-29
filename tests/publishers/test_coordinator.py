from uuid import UUID

import pytest
from asynctest import MagicMock

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import (
    PublicationStatus,
    Publication as PublicationModel,
)
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.abstract import EventPublication
from mobilizon_reshare.publishers.coordinator import (
    PublisherCoordinatorReport,
    PublicationReport,
    PublisherCoordinator,
    PublicationFailureNotifiersCoordinator,
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
async def mock_publications(
    num_publications: int,
    test_event: MobilizonEvent,
    mock_publisher_valid,
    mock_formatter_valid,
):
    result = []
    for i in range(num_publications):
        event = test_event.to_model()
        await event.save()
        publisher = Publisher(name="telegram")
        await publisher.save()
        publication = PublicationModel(
            id=UUID(int=i + 1),
            status=PublicationStatus.WAITING,
            event=event,
            publisher=publisher,
            timestamp=None,
            reason=None,
        )
        await publication.save()
        publication = EventPublication.from_orm(publication, test_event)
        publication.publisher = mock_publisher_valid
        publication.formatter = mock_formatter_valid
        result.append(publication)
    return result


@pytest.mark.parametrize("num_publications", [2])
@pytest.mark.asyncio
async def test_coordinator_run_success(mock_publications,):
    coordinator = PublisherCoordinator(publications=mock_publications,)
    report = coordinator.run()
    assert len(report.reports) == 2
    assert report.successful, "\n".join(
        map(lambda rep: rep.reason, report.reports.values())
    )


@pytest.mark.parametrize("num_publications", [1])
@pytest.mark.asyncio
async def test_coordinator_run_failure(
    mock_publications, mock_publisher_invalid, mock_formatter_invalid
):
    for pub in mock_publications:
        pub.publisher = mock_publisher_invalid
        pub.formatter = mock_formatter_invalid
    coordinator = PublisherCoordinator(mock_publications)

    report = coordinator.run()
    assert len(report.reports) == 1
    assert not report.successful
    assert (
        list(report.reports.values())[0].reason
        == "Invalid credentials, Invalid event, Invalid message"
    )


@pytest.mark.parametrize("num_publications", [1])
@pytest.mark.asyncio
async def test_coordinator_run_failure_response(
    mock_publications, mock_publisher_invalid_response
):

    for pub in mock_publications:
        pub.publisher = mock_publisher_invalid_response
    coordinator = PublisherCoordinator(publications=mock_publications)
    report = coordinator.run()
    assert len(report.reports) == 1
    assert not report.successful
    assert list(report.reports.values())[0].reason == "Invalid response"


@pytest.mark.asyncio
async def test_notifier_coordinator_publication_failed(mock_publisher_valid):
    mock_send = MagicMock()
    mock_publisher_valid._send = mock_send
    report = PublicationReport(
        status=PublicationStatus.FAILED,
        reason="some failure",
        publication_id=UUID(int=1),
    )
    coordinator = PublicationFailureNotifiersCoordinator(
        report, [mock_publisher_valid, mock_publisher_valid]
    )
    coordinator.notify_failure()

    # 4 = 2 reports * 2 notifiers
    assert mock_send.call_count == 2
