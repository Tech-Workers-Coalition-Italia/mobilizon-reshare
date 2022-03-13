import uuid

import arrow
import pytest
from click.testing import CliRunner

import mobilizon_reshare.publishers
import mobilizon_reshare.storage.query.read
from mobilizon_reshare.models.publisher import Publisher
import mobilizon_reshare.main.recap
from mobilizon_reshare.publishers import coordinator
from tests import today


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
        "updatedAt": "2021-05-23T12:15:00Z",
    }


def second_event_element():
    return {
        "beginsOn": "2021-06-07T05:00:00Z",
        "description": "desc_1",
        "endsOn": "2021-06-07T07:00:00Z",
        "onlineAddress": None,
        "options": {"showEndTime": True, "showStartTime": True},
        "physicalAddress": "loc_1",
        "picture": "https://example.org/thumblink_1",
        "title": "event_1",
        "url": "https://example.org/moblink_1",
        "uuid": str(uuid.UUID(int=1)),
        "updatedAt": "2021-06-07T05:00:00Z",
    }


@pytest.fixture
def mobilizon_answer(elements):
    return {"data": {"group": {"organizedEvents": {"elements": elements}}}}


@pytest.fixture
async def mock_now(monkeypatch):
    def _mock_now():
        return arrow.get(today)

    monkeypatch.setattr(mobilizon_reshare.main.recap, "now", _mock_now)

    return arrow.get(today)


@pytest.fixture
async def mock_publisher_config(monkeypatch, publisher_class, mock_formatter_class):
    # FIXME: This is subtly bound to the name field of publisher_class
    p = Publisher(name="mock")
    await p.save()

    def _mock_active_pub():
        return ["mock"]

    def _mock_pub_class(name):
        return publisher_class

    def _mock_format_class(name):
        return mock_formatter_class

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
        mobilizon_reshare.storage.query.read, "get_active_publishers", _mock_active_pub
    )

    monkeypatch.setattr(
        mobilizon_reshare.main.recap, "get_active_publishers", _mock_active_pub
    )
    monkeypatch.setattr(
        mobilizon_reshare.main.recap,
        "get_publisher_class",
        _mock_pub_class,
    )
    monkeypatch.setattr(
        mobilizon_reshare.main.recap,
        "get_formatter_class",
        _mock_format_class,
    )
    return p


@pytest.fixture
async def mock_notifier_config(monkeypatch, publisher_class, mock_formatter_class):
    def _mock_active_notifier():
        return ["test", "test2"]

    def _mock_notifier_class(name):
        return publisher_class

    def _mock_format_class(name):
        return mock_formatter_class

    monkeypatch.setattr(
        coordinator,
        "get_notifier_class",
        _mock_notifier_class,
    )
    monkeypatch.setattr(
        mobilizon_reshare.publishers.platforms.platform_mapping,
        "get_formatter_class",
        _mock_format_class,
    )

    monkeypatch.setattr(coordinator, "get_active_notifiers", _mock_active_notifier)


@pytest.fixture
def runner():
    return CliRunner()
