import importlib.resources
import os
from collections import UserList
from datetime import datetime, timedelta, timezone
from uuid import UUID

import arrow
import pytest
import responses
from tortoise.contrib.test import finalizer, initializer

import mobilizon_reshare
from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.notification import Notification, NotificationStatus
from mobilizon_reshare.models.publication import Publication, PublicationStatus
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.publishers.exceptions import PublisherError, InvalidResponse


def generate_publication_status(published):
    return PublicationStatus.COMPLETED if published else PublicationStatus.WAITING


def generate_event_status(published):
    return (
        EventPublicationStatus.COMPLETED
        if published
        else EventPublicationStatus.WAITING
    )


def generate_notification_status(published):
    return NotificationStatus.COMPLETED if published else NotificationStatus.WAITING


@pytest.fixture(scope="session", autouse=True)
def set_dynaconf_environment(request) -> None:
    os.environ["ENV_FOR_DYNACONF"] = "testing"
    os.environ["FORCE_ENV_FOR_DYNACONF"] = "testing"

    yield None

    os.environ["ENV_FOR_DYNACONF"] = ""
    os.environ["FORCE_ENV_FOR_DYNACONF"] = ""


@pytest.fixture
def event_generator():
    def _event_generator(
        begin_date=arrow.Arrow(year=2021, month=1, day=1, hour=11, minute=30),
        published=False,
        publication_time=None,
        mobilizon_id=UUID(int=12345),
    ):

        return MobilizonEvent(
            name="test event",
            description="description of the event",
            begin_datetime=begin_date,
            end_datetime=begin_date.shift(hours=2),
            mobilizon_link="http://some_link.com/123",
            mobilizon_id=mobilizon_id,
            thumbnail_link="http://some_link.com/123.jpg",
            location="location",
            status=generate_event_status(published),
            publication_time=publication_time
            or (begin_date.shift(days=-1) if published else None),
        )

    return _event_generator


@pytest.fixture()
def event() -> MobilizonEvent:
    begin_date = arrow.get(
        datetime(
            year=2021,
            month=1,
            day=1,
            hour=11,
            minute=30,
            tzinfo=timezone(timedelta(hours=1)),
        )
    )
    return MobilizonEvent(
        name="test event",
        description="description of the event",
        begin_datetime=begin_date,
        end_datetime=begin_date.shift(hours=1),
        mobilizon_link="http://some_link.com/123",
        mobilizon_id=UUID(int=12345),
        thumbnail_link="http://some_link.com/123.jpg",
        location="location",
    )


@pytest.fixture(scope="function", autouse=True)
def initialize_db_tests() -> None:
    db_url = os.environ.get("TORTOISE_TEST_DB", "sqlite://:memory:")
    initializer(
        [
            "mobilizon_reshare.models.event",
            "mobilizon_reshare.models.notification",
            "mobilizon_reshare.models.publication",
            "mobilizon_reshare.models.publisher",
        ],
        db_url=db_url,
        app_label="models",
    )
    with importlib.resources.path(
        mobilizon_reshare, ".secrets.toml"
    ) as bundled_secrets_path:
        os.environ["SECRETS_FOR_DYNACONF"] = str(bundled_secrets_path)

        yield None

        os.environ["SECRETS_FOR_DYNACONF"] = ""
        finalizer()


@pytest.fixture()
def event_model_generator():
    def _event_model_generator(
        idx=1,
        begin_date=datetime(
            year=2021,
            month=1,
            day=1,
            hour=11,
            minute=30,
            tzinfo=timezone(timedelta(hours=0)),
        ),
    ):
        return Event(
            name=f"event_{idx}",
            description=f"desc_{idx}",
            mobilizon_id=UUID(int=idx),
            mobilizon_link=f"moblink_{idx}",
            thumbnail_link=f"thumblink_{idx}",
            location=f"loc_{idx}",
            begin_datetime=begin_date,
            end_datetime=begin_date + timedelta(hours=2),
        )

    return _event_model_generator


@pytest.fixture()
def publisher_model_generator():
    def _publisher_model_generator(idx=1,):
        return Publisher(name=f"publisher_{idx}", account_ref=f"account_ref_{idx}")

    return _publisher_model_generator


@pytest.fixture()
def publication_model_generator():
    def _publication_model_generator(
        status=PublicationStatus.COMPLETED,
        publication_time=datetime(year=2021, month=1, day=1, hour=11, minute=30),
        event_id=None,
        publisher_id=None,
    ):
        return Publication(
            status=status,
            timestamp=publication_time,
            event_id=event_id,
            publisher_id=publisher_id,
        )

    return _publication_model_generator


@pytest.fixture()
def notification_model_generator():
    def _notification_model_generator(
        idx=1, published=False, publication_id=None, target_id=None
    ):
        return Notification(
            status=generate_notification_status(published),
            message=f"message_{idx}",
            publication_id=publication_id,
            target_id=target_id,
        )

    return _notification_model_generator


@pytest.fixture()
def message_collector():
    class MessageCollector(UserList):
        def collect_message(self, message):
            self.append(message)

    return MessageCollector()


@pytest.fixture
def mock_publisher_class(message_collector):
    class MockPublisher(AbstractPlatform):
        name = "mock"

        def _send(self, message, event):
            message_collector.append(message)

        def _validate_response(self, response):
            pass

        def validate_credentials(self) -> None:
            pass

    return MockPublisher


@pytest.fixture
def mock_publisher_valid(message_collector, mock_publisher_class):

    return mock_publisher_class()


@pytest.fixture
def mobilizon_url():
    return get_settings()["source"]["mobilizon"]["url"]


@responses.activate
@pytest.fixture
def mock_mobilizon_success_answer(mobilizon_answer, mobilizon_url):
    with responses.RequestsMock() as rsps:

        rsps.add(
            responses.POST, mobilizon_url, json=mobilizon_answer, status=200,
        )
        yield


@pytest.fixture
def mock_publication_window(publication_window):
    begin, end = publication_window
    get_settings().update(
        {"publishing.window.begin": begin, "publishing.window.end": end}
    )


@pytest.fixture
def mock_formatter_class():
    class MockFormatter(AbstractEventFormatter):
        def validate_event(self, event) -> None:
            pass

        def get_message_from_event(self, event) -> str:
            return f"{event.name}|{event.description}"

        def validate_message(self, event) -> None:
            pass

        def get_recap_fragment(self, event):
            return event.name

        def get_recap_header(self):
            return "Upcoming"

    return MockFormatter


@pytest.fixture
def mock_formatter_valid(mock_formatter_class):

    return mock_formatter_class()


@pytest.fixture
def mock_publisher_invalid_class(message_collector):
    class MockPublisher(AbstractPlatform):

        name = "mock"

        def _send(self, message, event):
            message_collector.append(message)

        def _validate_response(self, response):
            return InvalidResponse("response error")

        def validate_credentials(self) -> None:
            raise PublisherError("credentials error")

    return MockPublisher


@pytest.fixture
def mock_publisher_invalid(mock_publisher_invalid_class):

    return mock_publisher_invalid_class()
