import uuid

import pytest

import mobilizon_reshare.publishers
from mobilizon_reshare.models import event
from mobilizon_reshare.models.publisher import Publisher
import mobilizon_reshare.main.recap


def simple_event_element():
    return {
        "beginsOn": "2021-05-23T12:15:00Z",
        "description": "Some description",
        "endsOn": "2021-05-23T15:15:00Z",
        "onlineAddress": None,
        "options": {"showEndTime": True, "showStartTime": True},
        "physicalAddress": None,
        "picture": None,
        "title": "test event",
        "url": "https://some_mobilizon/events/1e2e5943-4a5c-497a-b65d-90457b715d7b",
        "uuid": str(uuid.uuid4()),
    }


@pytest.fixture
def mobilizon_answer(elements):
    return {"data": {"group": {"organizedEvents": {"elements": elements}}}}


@pytest.fixture
async def mock_publisher_config(
    monkeypatch, mock_publisher_class, mock_formatter_class
):
    p = Publisher(name="test")
    await p.save()

    p2 = Publisher(name="test2")
    await p2.save()

    def _mock_active_pub():
        return ["test", "test2"]

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

    monkeypatch.setattr(
        mobilizon_reshare.main.recap, "get_active_publishers", _mock_active_pub
    )
    monkeypatch.setattr(
        mobilizon_reshare.main.recap, "get_publisher_class", _mock_pub_class,
    )
    monkeypatch.setattr(
        mobilizon_reshare.main.recap, "get_formatter_class", _mock_format_class,
    )
    return p
