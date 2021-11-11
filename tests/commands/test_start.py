from logging import DEBUG

import pytest

import mobilizon_reshare.publishers.platforms.platform_mapping
from mobilizon_reshare.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_reshare.main.start import start
from mobilizon_reshare.models import event
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.models.publisher import Publisher

simple_event_element = {
    "beginsOn": "2021-05-23T12:15:00Z",
    "description": "Some description",
    "endsOn": "2021-05-23T15:15:00Z",
    "onlineAddress": None,
    "options": {"showEndTime": True, "showStartTime": True},
    "physicalAddress": None,
    "picture": None,
    "title": "test event",
    "url": "https://some_mobilizon/events/1e2e5943-4a5c-497a-b65d-90457b715d7b",
    "uuid": "1e2e5943-4a5c-497a-b65d-90457b715d7b",
}
simple_event_response = {
    "data": {"group": {"organizedEvents": {"elements": [simple_event_element]}}}
}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mobilizon_answer", [{"data": {"group": {"organizedEvents": {"elements": []}}}}],
)
async def test_start_no_event(mock_mobilizon_success_answer, mobilizon_answer, caplog):

    with caplog.at_level(DEBUG):
        assert await start() is None
        assert "No event to publish found" in caplog.text


@pytest.fixture
async def mock_publisher_config(
    monkeypatch, mock_publisher_class, mock_formatter_class
):
    p = Publisher(name="test")
    await p.save()

    def _mock_active_pub():
        return ["test"]

    def _mock_pub_class(name):
        return mock_publisher_class

    def _mock_format_class(name):
        return mock_formatter_class

    monkeypatch.setattr(event, "get_active_publishers", _mock_active_pub)
    monkeypatch.setattr(
        mobilizon_reshare.publishers.platforms.platform_mapping,
        "get_publisher_class",
        _mock_pub_class,
    )
    monkeypatch.setattr(
        mobilizon_reshare.publishers.platforms.platform_mapping,
        "get_formatter_class",
        _mock_format_class,
    )
    return p


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mobilizon_answer", [simple_event_response],
)
@pytest.mark.parametrize("publication_window", [(0, 24)])
async def test_start_new_event(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    mock_publication_window,
    message_collector,
):

    with caplog.at_level(DEBUG):
        assert await start() is None

        assert "Event to publish found" in caplog.text
        assert message_collector == ["test event|Some description"]

        all_events = (
            await Event.all()
            .prefetch_related("publications")
            .prefetch_related("publications__publisher")
        )

        assert len(all_events) == 1, all_events

        publications = all_events[0].publications
        assert len(publications) == 1, publications

        assert publications[0].status == PublicationStatus.COMPLETED
        assert (
            MobilizonEvent.from_model(all_events[0]).status
            == EventPublicationStatus.COMPLETED
        )
