from datetime import datetime

import pytest
from jinja2 import Template

from mobilizon_bots.event.event import MobilizonEvent


@pytest.fixture()
def event() -> MobilizonEvent:
    return MobilizonEvent(
        name="test event",
        description="description of the event",
        begin_datetime=datetime(year=2021, month=1, day=1, hour=11, minute=30),
        end_datetime=datetime(year=2021, month=1, day=1, hour=12, minute=30),
        last_accessed=datetime.now(),
        mobilizon_link="http://some_link.com/123",
        mobilizon_id="12345",
        thumbnail_link="http://some_link.com/123.jpg",
        location="location",
    )


@pytest.fixture()
def simple_template():
    return Template(
        "{{name}}|{{description}}|{{location}}|{{begin_datetime.strftime('%Y-%m-%d, %H:%M')}}"
    )


def test_fill_template(event, simple_template):
    assert (
        event._fill_template(simple_template)
        == "test event|description of the event|location|2021-01-01, 11:30"
    )


def test_format(event, simple_template):
    assert (
        event.format(simple_template)
        == "test event|description of the event|location|2021-01-01, 11:30"
    )
