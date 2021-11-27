import logging
from uuid import UUID

import pytest
from asynctest import MagicMock

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import (
    PublicationStatus,
    Publication as PublicationModel,
)
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.abstract import EventPublication, RecapPublication
from mobilizon_reshare.publishers.coordinator import (
    PublisherCoordinatorReport,
    EventPublicationReport,
    PublisherCoordinator,
    PublicationFailureNotifiersCoordinator,
    RecapCoordinator,
)


@pytest.fixture()
def failure_report(mock_publisher_invalid):
    return EventPublicationReport(
        status=PublicationStatus.FAILED,
        reason="some failure",
        publication=EventPublication(
            publisher=mock_publisher_invalid, formatter=None, event=None, id=UUID(int=1)
        ),
    )


@pytest.mark.parametrize(
    "statuses, successful",
    [
        [[PublicationStatus.COMPLETED, PublicationStatus.COMPLETED], True],
        [[PublicationStatus.COMPLETED, PublicationStatus.FAILED], False],
        [[], True],
        [[PublicationStatus.COMPLETED], True],
    ],
)
def test_publication_report_successful(statuses, successful):
    reports = []
    for i, status in enumerate(statuses):
        reports.append(
            EventPublicationReport(reason=None, publication=None, status=status)
        )
    assert (
        PublisherCoordinatorReport(publications=[], reports=reports).successful
        == successful
    )


@pytest.fixture
@pytest.mark.asyncio
async def mock_recap_publications(
    num_publications: int,
    test_event: MobilizonEvent,
    mock_publisher_valid,
    mock_formatter_valid,
):
    result = []
    for _ in range(num_publications):
        result.append(
            RecapPublication(
                publisher=mock_publisher_valid,
                formatter=mock_formatter_valid,
                events=[test_event, test_event],
            )
        )

    return result


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
            event=event,
            publisher=publisher,
            timestamp=None,
            reason=None,
        )
        publication = EventPublication.from_orm(publication, test_event)
        publication.publisher = mock_publisher_valid
        publication.formatter = mock_formatter_valid
        result.append(publication)
    return result


@pytest.mark.parametrize("num_publications", [2])
@pytest.mark.asyncio
async def test_publication_coordinator_run_success(
    mock_publications,
):
    coordinator = PublisherCoordinator(
        publications=mock_publications,
    )
    report = coordinator.run()
    assert len(report.reports) == 2
    assert report.successful, "\n".join(map(lambda rep: rep.reason, report.reports))


@pytest.mark.parametrize("num_publications", [1])
@pytest.mark.asyncio
async def test_publication_coordinator_run_failure(
    mock_publications, mock_publisher_invalid, mock_formatter_invalid
):
    for pub in mock_publications:
        pub.publisher = mock_publisher_invalid
        pub.formatter = mock_formatter_invalid
    coordinator = PublisherCoordinator(mock_publications)

    report = coordinator.run()
    assert len(report.reports) == 1
    assert not report.successful
    assert list(report.reports)[0].reason == "credentials error, Invalid event error"


@pytest.mark.parametrize("num_publications", [1])
@pytest.mark.asyncio
async def test_publication_coordinator_run_failure_response(
    mock_publications, mock_publisher_invalid_response
):

    for pub in mock_publications:
        pub.publisher = mock_publisher_invalid_response
    coordinator = PublisherCoordinator(publications=mock_publications)
    report = coordinator.run()
    assert len(report.reports) == 1
    assert not report.successful
    assert list(report.reports)[0].reason == "Invalid response"


@pytest.mark.asyncio
async def test_notifier_coordinator_publication_failed(
    mock_publisher_valid, failure_report
):
    mock_send = MagicMock()
    mock_publisher_valid._send = mock_send
    coordinator = PublicationFailureNotifiersCoordinator(
        failure_report, [mock_publisher_valid, mock_publisher_valid]
    )
    coordinator.notify_failure()

    # 4 = 2 reports * 2 notifiers
    assert mock_send.call_count == 2


@pytest.mark.asyncio
async def test_notifier_coordinator_error(
    failure_report, mock_publisher_invalid_response, caplog
):
    mock_send = MagicMock()
    mock_publisher_invalid_response._send = mock_send

    coordinator = PublicationFailureNotifiersCoordinator(
        failure_report,
        [mock_publisher_invalid_response, mock_publisher_invalid_response],
    )
    with caplog.at_level(logging.CRITICAL):
        coordinator.notify_failure()
        assert "Notifier failed to send" in caplog.text
        assert failure_report.get_failure_message() in caplog.text
    # 4 = 2 reports * 2 notifiers
    assert mock_send.call_count == 2


@pytest.mark.parametrize("num_publications", [2])
@pytest.mark.asyncio
async def test_recap_coordinator_run_success(
    mock_recap_publications, message_collector
):
    coordinator = RecapCoordinator(recap_publications=mock_recap_publications)
    report = coordinator.run()

    # one recap per publication
    assert len(message_collector) == 2

    # check that header is in all messages
    assert all(("Upcoming" in message) for message in message_collector)

    assert len(report.reports) == 2
    assert report.successful, "\n".join(map(lambda rep: rep.reason, report.reports))
