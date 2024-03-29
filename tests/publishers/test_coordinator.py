import logging
from datetime import timedelta
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from mobilizon_reshare.dataclasses import MobilizonEvent
from mobilizon_reshare.dataclasses.publication import (
    _EventPublication,
    RecapPublication,
)
from mobilizon_reshare.models.publication import (
    PublicationStatus,
    Publication as PublicationModel,
)
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.coordinators.event_publishing.notify import (
    PublicationFailureNotifiersCoordinator,
)
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    EventPublicationReport,
    PublisherCoordinatorReport,
    PublisherCoordinator,
)
from mobilizon_reshare.publishers.coordinators.recap_publishing.recap import (
    RecapCoordinator,
)
from tests import today


@pytest.fixture()
def failure_report(mock_publisher_invalid, event):
    return EventPublicationReport(
        status=PublicationStatus.FAILED,
        reason="some failure",
        publication=_EventPublication(
            publisher=mock_publisher_invalid,
            formatter=None,
            event=event,
            id=UUID(int=1),
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
    for _, status in enumerate(statuses):
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
            timestamp=today + timedelta(hours=i),
            reason=None,
        )
        publication = _EventPublication.from_orm(publication, test_event)
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


@pytest.mark.parametrize("num_publications", [2])
@pytest.mark.asyncio
async def test_publication_coordinator_run_partial_failure(
    mock_publications, mock_publisher_invalid, mock_formatter_invalid
):

    mock_publications[0].publisher = mock_publisher_invalid
    mock_publications[0].formatter = mock_formatter_invalid
    coordinator = PublisherCoordinator(mock_publications)

    report = coordinator.run()
    assert len(report.reports) == 2
    assert not list(report.reports)[0].successful
    assert list(report.reports)[0].reason == "credentials error, Invalid event error"
    assert list(report.reports)[1].successful
    assert list(report.reports)[1].reason is None


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
    mock_zulip_publisher, failure_report
):
    mock_send = MagicMock()
    mock_zulip_publisher._send = mock_send
    coordinator = PublicationFailureNotifiersCoordinator(
        failure_report, [mock_zulip_publisher, mock_zulip_publisher]
    )
    coordinator.notify_failure()

    # 4 = 2 reports * 2 notifiers
    assert mock_send.call_count == 2


@pytest.mark.asyncio
async def test_notifier_coordinator_error(
    failure_report, mock_zulip_publisher_invalid_response, caplog
):
    mock_send = MagicMock()
    mock_zulip_publisher_invalid_response._send = mock_send

    coordinator = PublicationFailureNotifiersCoordinator(
        failure_report,
        [mock_zulip_publisher_invalid_response, mock_zulip_publisher_invalid_response],
    )
    with caplog.at_level(logging.CRITICAL):
        coordinator.notify_failure()
        assert "Failed to notify failure of" in caplog.text
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
