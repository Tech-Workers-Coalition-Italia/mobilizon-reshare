from datetime import datetime, timedelta, timezone

import arrow
import pytest
import tortoise.timezone

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.models.event import Event


@pytest.mark.asyncio
async def test_event_create(event_model_generator):
    event_model = event_model_generator()
    await event_model.save()
    event_db = await Event.filter(name="event_1").first()
    assert event_db.begin_datetime == datetime(
        year=2021,
        month=1,
        day=1,
        hour=11,
        minute=30,
        tzinfo=timezone(timedelta(hours=0)),
    )


@pytest.mark.asyncio
async def test_event_timezone_storage(event_model_generator):
    cet = timezone(timedelta(hours=1))
    event_cet = event_model_generator(
        begin_date=datetime(year=2021, month=6, day=6, hour=5, minute=0, tzinfo=cet),
    )
    await event_cet.save()
    cest = timezone(timedelta(hours=2))
    event_cest = event_model_generator(
        idx=2,
        begin_date=datetime(year=2021, month=6, day=6, hour=6, minute=0, tzinfo=cest),
    )
    await event_cest.save()
    events = await Event.all()
    assert len(events) == 2
    assert events[0].begin_datetime == events[1].begin_datetime


@pytest.mark.asyncio
async def test_event_sort_by_date(event_model_generator):
    today = datetime(
        2021,
        5,
        10,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=timezone(timedelta(hours=1)),
    )
    today_utc = datetime(
        2021,
        5,
        9,
        hour=23,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=timezone(timedelta(hours=0)),
    )
    event_yesterday = event_model_generator(idx=1, begin_date=today - timedelta(days=1))
    event_today = event_model_generator(idx=2, begin_date=today)
    event_tomorrow = event_model_generator(idx=3, begin_date=today + timedelta(days=1))

    await event_yesterday.save()
    await event_today.save()
    await event_tomorrow.save()

    events = await Event.all().order_by("begin_datetime")

    assert len(events) == 3

    assert (
        events[0].begin_datetime < events[1].begin_datetime < events[2].begin_datetime
    )

    assert events[0].begin_datetime == today_utc - timedelta(days=1)
    assert events[1].begin_datetime == today_utc
    assert events[2].begin_datetime == today_utc + timedelta(days=1)


@pytest.mark.asyncio
async def test_mobilizon_event_to_model(event):
    event_model = event.to_model()
    await event_model.save()

    event_db = await Event.all().first()
    begin_date_utc = arrow.Arrow(year=2021, month=1, day=1, hour=10, minute=30)
    begin_date_utc = begin_date_utc.astimezone(tortoise.timezone.get_default_timezone())

    assert event_db.name == "test event"
    assert event_db.description == "description of the event"
    assert event_db.begin_datetime == begin_date_utc
    assert event_db.end_datetime == begin_date_utc + timedelta(hours=1)
    assert event_db.mobilizon_link == "http://some_link.com/123"
    assert event_db.mobilizon_id == "12345"
    assert event_db.thumbnail_link == "http://some_link.com/123.jpg"
    assert event_db.location == "location"


@pytest.mark.asyncio
async def test_mobilizon_event_from_model(event_model_generator):
    event_model = event_model_generator()
    await event_model.save()

    event_db = await Event.all().first()
    event = MobilizonEvent.from_model(event=event_db, tz="CET")

    begin_date_utc = arrow.Arrow(year=2021, month=1, day=1, hour=11, minute=30)

    assert event.name == "event_1"
    assert event.description == "desc_1"
    assert event.begin_datetime == begin_date_utc
    assert event.end_datetime == begin_date_utc.shift(hours=2)
    assert event.mobilizon_link == "moblink_1"
    assert event.mobilizon_id == "mobid_1"
    assert event.thumbnail_link == "thumblink_1"
    assert event.location == "loc_1"
