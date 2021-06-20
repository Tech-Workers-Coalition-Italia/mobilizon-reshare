import arrow
import pkg_resources
import os
from datetime import datetime, timedelta, timezone

import pytest

from dynaconf import settings
from tortoise.contrib.test import finalizer, initializer

from mobilizon_bots.config.config import build_and_validate_settings

from mobilizon_bots.event.event import (
    MobilizonEvent,
    NotificationStatus,
)
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.notification import Notification
from mobilizon_bots.models.publication import Publication, PublicationStatus
from mobilizon_bots.models.publisher import Publisher


def generate_publication_status(published):
    return PublicationStatus.COMPLETED if published else PublicationStatus.WAITING


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    config_file = pkg_resources.resource_filename(
        "tests.resources", "test_settings.toml"
    )

    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    build_and_validate_settings([config_file])


def generate_notification_status(published):
    return NotificationStatus.COMPLETED if published else NotificationStatus.WAITING


@pytest.fixture
def event_generator():
    def _event_generator(
        begin_date=arrow.Arrow(year=2021, month=1, day=1, hour=11, minute=30),
        published=False,
        publication_time=None,
    ):

        return MobilizonEvent(
            name="test event",
            description="description of the event",
            begin_datetime=begin_date,
            end_datetime=begin_date.shift(hours=2),
            mobilizon_link="http://some_link.com/123",
            mobilizon_id="12345",
            thumbnail_link="http://some_link.com/123.jpg",
            location="location",
            publication_status=generate_publication_status(published),
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
        mobilizon_id="12345",
        thumbnail_link="http://some_link.com/123.jpg",
        location="location",
    )


@pytest.fixture(scope="function", autouse=True)
def initialize_db_tests(request) -> None:
    db_url = os.environ.get("TORTOISE_TEST_DB", "sqlite://:memory:")
    initializer(
        [
            "mobilizon_bots.models.event",
            "mobilizon_bots.models.notification",
            "mobilizon_bots.models.publication",
            "mobilizon_bots.models.publisher",
        ],
        db_url=db_url,
        app_label="models",
    )
    request.addfinalizer(finalizer)


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
            mobilizon_id=f"mobid_{idx}",
            mobilizon_link=f"moblink_{idx}",
            thumbnail_link=f"thumblink_{idx}",
            location=f"loc_{idx}",
            begin_datetime=begin_date,
            end_datetime=begin_date + timedelta(hours=2),
        )

    return _event_model_generator


@pytest.fixture()
def publisher_model_generator():
    def _publisher_model_generator(
        idx=1,
    ):
        return Publisher(name=f"publisher_{idx}", account_ref=f"account_ref_{idx}")

    return _publisher_model_generator


@pytest.fixture()
def publication_model_generator():
    def _publication_model_generator(
        status=PublicationStatus.WAITING,
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
