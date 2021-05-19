import pytest

from datetime import datetime
from tortoise import timezone

from mobilizon_bots.models.event import Event


@pytest.mark.asyncio
async def test_event_create(event_model_generator):
    event_model = event_model_generator()
    await event_model.save()
    event_db = await Event.filter(name="event1").first()
    assert event_db.utcoffset == 360
    assert event_db.begin_datetime == datetime(
        2021,
        5,
        10,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=timezone.get_default_timezone(),
    )
