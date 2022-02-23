import importlib.resources
import os
from collections import UserList
from datetime import datetime, timedelta, timezone
from typing import Union
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
from mobilizon_reshare.storage.query.converter import event_to_model
from mobilizon_reshare.storage.query.write import get_publisher_by_name
from tests import today

with importlib.resources.path(
    mobilizon_reshare, ".secrets.toml"
) as bundled_secrets_path:
    os.environ["SECRETS_FOR_DYNACONF"] = str(bundled_secrets_path)


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
        last_update_time=arrow.Arrow(year=2021, month=1, day=1, hour=11, minute=30),
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
            last_update_time=last_update_time,
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
        last_update_time=begin_date,
    )


@pytest.fixture
async def stored_event(event):
    model = event_to_model(event)
    await model.save()
    await model.fetch_related("publications")
    return model


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
    yield None
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
            last_update_time=begin_date,
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


async def _generate_publishers(specification):

    publishers = []
    for i, publisher_name in enumerate(specification["publisher"]):
        publisher = Publisher(
            id=UUID(int=i), name=publisher_name, account_ref=f"account_ref_{i}"
        )
        publishers.append(publisher)
        await publisher.save()

    return publishers


async def _generate_events(specification):
    events = []
    if "event" in specification.keys():
        for i in range(specification["event"]):
            begin_date = today + timedelta(days=i)
            event = Event(
                id=UUID(int=i),
                name=f"event_{i}",
                description=f"desc_{i}",
                mobilizon_id=UUID(int=i),
                mobilizon_link=f"moblink_{i}",
                thumbnail_link=f"thumblink_{i}",
                location=f"loc_{i}",
                begin_datetime=begin_date,
                end_datetime=begin_date + timedelta(hours=2),
                last_update_time=begin_date,
            )
            events.append(event)
            await event.save()
    return events


async def _generate_publications(events, publishers, specification):
    if "publications" in specification.keys():
        for i, publication in enumerate(specification["publications"]):
            status = publication.get("status", PublicationStatus.COMPLETED)
            timestamp = publication.get("timestamp", today + timedelta(hours=i))
            await Publication.create(
                id=UUID(int=i),
                status=status,
                timestamp=timestamp,
                event_id=events[publication["event_idx"]].id,
                publisher_id=publishers[publication["publisher_idx"]].id,
            )


@pytest.fixture(scope="module")
def generate_models():
    async def _generate_models(specification: dict[str, Union[int, list]]):
        publishers = await _generate_publishers(specification)
        events = await _generate_events(specification)
        await _generate_publications(events, publishers, specification)

    return _generate_models


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


@pytest.fixture
async def event_with_failed_publication(
    stored_event, mock_publisher_config, failed_publication
):
    return stored_event


@pytest.fixture
async def failed_publication(stored_event):

    p = Publication(
        event=stored_event,
        status=PublicationStatus.FAILED,
        timestamp=arrow.now().datetime,
        publisher=await get_publisher_by_name("mock"),
    )
    await p.save()
    return p
