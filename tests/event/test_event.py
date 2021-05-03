from datetime import timedelta, datetime

import pytest
from mobilizon_bots.event.event import MobilizonEvent


@pytest.fixture()
def event() -> MobilizonEvent:
    return MobilizonEvent(
        name="test event",
        description="description of the event",
        begin_datetime=datetime.now() + timedelta(days=1),
        end_datetime=datetime.now() + timedelta(days=1, hours=2),
        last_accessed=datetime.now(),
        mobilizon_link="http://some_link.com/123",
        mobilizon_id="12345",
        thumbnail_link="http://some_link.com/123.jpg",
        location="location",
    )


def test_fill_template(event):
    assert (
        event._fill_template("{name}|{description}|{location}")
        == "test event|description of the event|location"
    )


def test_format(event):
    assert (
        event.format("{name}|{description}|{location}")
        == "test event|description of the event|location"
    )
