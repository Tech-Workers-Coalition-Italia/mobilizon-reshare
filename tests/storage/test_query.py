from datetime import datetime, timedelta, timezone

import arrow
import pytest

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.models.publication import PublicationStatus

from mobilizon_bots.storage.query import (
    get_published_events,
    get_unpublished_events,
    create_unpublished_events,
)


@pytest.fixture(scope="module")
def setup():
    async def _setup(
        publisher_model_generator, publication_model_generator, event_model_generator
    ):
        today = datetime(
            year=2021,
            month=6,
            day=6,
            hour=5,
            minute=0,
            tzinfo=timezone(timedelta(hours=2)),
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
            status=PublicationStatus.WAITING,
        )
        await publication_1.save()
        await publication_2.save()
        await publication_3.save()
        await publication_4.save()
        return (
            [event_1, event_2, event_3],
            [publication_1, publication_2, publication_3, publication_4],
            [publisher_1, publisher_2],
            today,
        )

    return _setup


@pytest.mark.asyncio
async def test_get_published_events(
    publisher_model_generator, publication_model_generator, event_model_generator, setup
):
    events, publications, publishers, today = await setup(
        publisher_model_generator, publication_model_generator, event_model_generator
    )

    published_events = list(await get_published_events())
    assert len(published_events) == 1

    assert published_events[0].name == events[0].name

    assert published_events[0].begin_datetime == arrow.get(today)


@pytest.mark.asyncio
async def test_get_unpublished_events(
    publisher_model_generator, publication_model_generator, event_model_generator, setup
):
    events, publications, publishers, today = await setup(
        publisher_model_generator, publication_model_generator, event_model_generator
    )

    published_events = list(await get_unpublished_events())
    assert len(published_events) == 2

    assert published_events[0].name == events[2].name
    assert published_events[1].name == events[0].name
    assert published_events[0].begin_datetime == events[2].begin_datetime
    assert published_events[1].begin_datetime == events[0].begin_datetime


@pytest.mark.asyncio
async def test_create_unpublished_events(
    publisher_model_generator,
    publication_model_generator,
    event_model_generator,
    event_generator,
    setup,
):
    events, publications, publishers, today = await setup(
        publisher_model_generator, publication_model_generator, event_model_generator
    )

    event_4 = event_generator(begin_date=arrow.get(today + timedelta(days=6)))
    event_5 = event_generator(
        begin_date=arrow.get(today + timedelta(days=12)), mobilizon_id="67890"
    )

    await events[0].fetch_related("publications")
    await events[0].fetch_related("publications__publisher")
    events_from_internet = [MobilizonEvent.from_model(events[0]), event_4, event_5]

    await create_unpublished_events(
        unpublished_mobilizon_events=events_from_internet,
        active_publishers=["publisher_1", "publisher_2"],
    )
    unpublished_events = list(await get_unpublished_events())

    assert len(unpublished_events) == 4
    assert unpublished_events[0].mobilizon_id == "mobid_3"
    assert unpublished_events[1].mobilizon_id == "mobid_1"
    assert unpublished_events[2].mobilizon_id == "12345"
    assert unpublished_events[3].mobilizon_id == "67890"
