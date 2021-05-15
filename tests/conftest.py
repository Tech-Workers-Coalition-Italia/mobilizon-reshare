import arrow
import pytest

from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus


def generate_publication_status(published):
    return PublicationStatus.COMPLETED if published else PublicationStatus.WAITING


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
            last_accessed=arrow.now(),
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
        last_accessed=arrow.now(),
        mobilizon_link="http://some_link.com/123",
        mobilizon_id="12345",
        thumbnail_link="http://some_link.com/123.jpg",
        location="location",
    )
