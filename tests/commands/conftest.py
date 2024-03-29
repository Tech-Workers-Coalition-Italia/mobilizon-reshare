import uuid

import arrow
import pytest
from click.testing import CliRunner

import mobilizon_reshare.publishers
import mobilizon_reshare.storage.query.read
from mobilizon_reshare.models.publisher import Publisher
import mobilizon_reshare.main.recap
from tests import today
from tests.conftest import event_1, event_0


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


def first_event_element():
    return {
        "beginsOn": event_0.begin_datetime.isoformat(),
        "description": "desc_0",
        "endsOn": event_0.end_datetime.isoformat(),
        "onlineAddress": None,
        "options": {"showEndTime": True, "showStartTime": True},
        "physicalAddress": {"description": "", "locality": "loc_0", "region": ""},
        "picture": {"url": "https://example.org/thumblink_0"},
        "title": "event_0",
        "url": "https://example.org/moblink_0",
        "uuid": str(uuid.UUID(int=0)),
        "updatedAt": event_0.last_update_time.isoformat(),
    }


def second_event_element():
    return {
        "beginsOn": event_1.begin_datetime.isoformat(),
        "description": "desc_1",
        "endsOn": event_1.end_datetime.isoformat(),
        "onlineAddress": None,
        "options": {"showEndTime": True, "showStartTime": True},
        "physicalAddress": {"description": "", "locality": "loc_1", "region": ""},
        "picture": {"url": "https://example.org/thumblink_1"},
        "title": "event_1",
        "url": "https://example.org/moblink_1",
        "uuid": str(uuid.UUID(int=1)),
        "updatedAt": event_1.last_update_time.isoformat(),
    }


@pytest.fixture
def mobilizon_answer(elements):
    return {"data": {"group": {"organizedEvents": {"elements": elements}}}}


@pytest.fixture
def multiple_answers(multiple_elements: list[list[dict]]):
    return [
        {"data": {"group": {"organizedEvents": {"elements": elements}}}}
        for elements in multiple_elements
    ]


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
        mobilizon_reshare.main.publish, "get_active_publishers", _mock_active_pub
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


@pytest.fixture
async def mock_notifier_config(monkeypatch, publisher_class, mock_formatter_class):
    def _mock_active_notifier():
        return ["test", "test2"]

    def _mock_notifier_class(name):
        return publisher_class

    def _mock_format_class(name):
        return mock_formatter_class

    monkeypatch.setattr(
        mobilizon_reshare.publishers.coordinators.event_publishing.notify,
        "get_notifier_class",
        _mock_notifier_class,
    )
    monkeypatch.setattr(
        mobilizon_reshare.publishers.coordinators.event_publishing.notify,
        "get_formatter_class",
        _mock_format_class,
    )
    monkeypatch.setattr(
        mobilizon_reshare.publishers.coordinators.event_publishing.notify,
        "get_notifier_class",
        _mock_notifier_class,
    )
    monkeypatch.setattr(
        mobilizon_reshare.publishers.platforms.platform_mapping,
        "get_formatter_class",
        _mock_format_class,
    )
    monkeypatch.setattr(
        mobilizon_reshare.publishers.coordinators.event_publishing.notify,
        "get_formatter_class",
        _mock_format_class,
    )

    monkeypatch.setattr(
        mobilizon_reshare.publishers.coordinators.event_publishing.notify,
        "get_active_notifiers",
        _mock_active_notifier,
    )
    monkeypatch.setattr(
        mobilizon_reshare.config.notifiers,
        "get_active_notifiers",
        lambda s: [],
    )


@pytest.fixture
def runner():
    return CliRunner()
