import arrow
import pkg_resources
import pytest
from dynaconf import settings

from mobilizon_bots.config.config import build_and_validate_settings
from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus


def generate_publication_status(published):
    return PublicationStatus.COMPLETED if published else PublicationStatus.WAITING


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    config_file = pkg_resources.resource_filename(
        "tests.resources", "test_settings.toml"
    )

    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")
    build_and_validate_settings([config_file])


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
    return MobilizonEvent(
        name="test event",
        description="description of the event",
        begin_datetime=arrow.Arrow(year=2021, month=1, day=1, hour=11, minute=30),
        end_datetime=arrow.Arrow(year=2021, month=1, day=1, hour=12, minute=30),
        mobilizon_link="http://some_link.com/123",
        mobilizon_id="12345",
        thumbnail_link="http://some_link.com/123.jpg",
        location="location",
    )
