from datetime import datetime, timedelta, timezone
from uuid import UUID

import arrow
import pytest

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.platforms.platform_mapping import get_formatter_class


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
        description="<p>description of the event</p>",
        begin_datetime=begin_date,
        end_datetime=begin_date.shift(hours=1),
        mobilizon_link="http://some_link.com/123",
        mobilizon_id=UUID(int=12345),
        thumbnail_link="http://some_link.com/123.jpg",
        location="location",
        last_update_time=begin_date,
    )


@pytest.mark.parametrize(
    "publisher_name,expected_output",
    [
        [
            "facebook",
            """# 

🕒 01 January, 11:30 - 01 January, 12:30


📍 location


description of the event

Link: http://some_link.com/123
""",
        ],
        [
            "telegram",
            """<strong>test event</strong>

🕒 01 January, 11:30 - 01 January, 12:30
📍 location

description of the event

<a href="http://some_link.com/123">Link</a>""",
        ],
    ],
)
def test_output_format(event, publisher_name, expected_output):
    assert (
        get_formatter_class(publisher_name)().get_message_from_event(event).strip()
        == expected_output.strip()
    )
