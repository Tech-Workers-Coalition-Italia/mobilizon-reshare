from datetime import datetime, timedelta, timezone

import arrow
import pytest

from mobilizon_bots.event.event import PublicationStatus
from mobilizon_bots.storage.query import get_published_events


@pytest.mark.asyncio
async def test_get_unpublished_events(
    publisher_model_generator, publication_model_generator, event_model_generator
):
    today = datetime(
        year=2021, month=6, day=6, hour=5, minute=0, tzinfo=timezone(timedelta(hours=2))
    )
    publisher_1 = publisher_model_generator()
    publisher_2 = publisher_model_generator(idx=2)
    await publisher_1.save()
    await publisher_2.save()

    event_1 = event_model_generator(begin_date=today)
    event_2 = event_model_generator(idx=2, begin_date=today + timedelta(days=2))
    event_3 = event_model_generator(idx=3, begin_date=today + timedelta(days=-2))
    await event_1.save()
    await event_2.save()
    await event_3.save()

    publication_1 = publication_model_generator(
        event_id=event_1.id, publisher_id=publisher_1.id
    )
    publication_2 = publication_model_generator(
        event_id=event_1.id,
        publisher_id=publisher_2.id,
        status=PublicationStatus.COMPLETED,
    )
    publication_3 = publication_model_generator(
        event_id=event_2.id,
        publisher_id=publisher_1.id,
        status=PublicationStatus.FAILED,
    )
    publication_4 = publication_model_generator(
        event_id=event_3.id,
        publisher_id=publisher_2.id,
        status=PublicationStatus.PARTIAL,
    )
    await publication_1.save()
    await publication_2.save()
    await publication_3.save()
    await publication_4.save()

    published_events = list(await get_published_events())
    assert len(published_events) == 2

    assert published_events[0].name == event_3.name
    assert published_events[1].name == event_1.name

    assert published_events[0].begin_datetime == arrow.get(today + timedelta(days=-2))
    assert published_events[1].begin_datetime == arrow.get(today)
