from datetime import datetime, timedelta, timezone

import arrow
import pytest

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import PublicationStatus, Publication
from mobilizon_bots.models.publisher import Publisher

from mobilizon_bots.storage.query import (
    get_published_events,
    get_unpublished_events,
    create_unpublished_events,
    get_mobilizon_event_publications,
    prefetch_event_relations,
)


today = datetime(
    year=2021,
    month=6,
    day=6,
    hour=5,
    minute=0,
    tzinfo=timezone(timedelta(hours=2)),
)

complete_specification = {
    "event": {"amount": 4},
    "publications": [
        {"event_idx": 0, "publisher_idx": 0},
        {
            "event_idx": 0,
            "publisher_idx": 1,
            "status": PublicationStatus.COMPLETED,
        },
        {
            "event_idx": 1,
            "publisher_idx": 0,
            "status": PublicationStatus.WAITING,
        },
        {
            "event_idx": 2,
            "publisher_idx": 2,
            "status": PublicationStatus.FAILED,
        },
        {
            "event_idx": 3,
            "publisher_idx": 2,
            "status": PublicationStatus.COMPLETED,
        },
    ],
}


@pytest.fixture(scope="module")
def generate_models():
    async def _generate_models(specification: dict[str, dict]):
        publishers = []
        for i in range(
            specification["publisher"]["amount"]
            if "publisher" in specification.keys()
            else 3
        ):
            publisher = Publisher(name=f"publisher_{i}", account_ref=f"account_ref_{i}")
            publishers.append(publisher)
            await publisher.save()

        events = []
        for i in range(specification["event"]["amount"]):
            begin_date = today + timedelta(days=i)
            event = Event(
                name=f"event_{i}",
                description=f"desc_{i}",
                mobilizon_id=f"mobid_{i}",
                mobilizon_link=f"moblink_{i}",
                thumbnail_link=f"thumblink_{i}",
                location=f"loc_{i}",
                begin_datetime=specification["event"].get("begin_datetime", begin_date),
                end_datetime=specification["event"].get(
                    "end_datetime", begin_date + timedelta(hours=2)
                ),
            )
            events.append(event)
            await event.save()

        for i in range(len(specification["publications"])):
            await Publication.create(
                status=specification["publications"][i].get(
                    "status", PublicationStatus.WAITING
                ),
                timestamp=specification["publications"][i].get(
                    "timestamp", today + timedelta(hours=i)
                ),
                event_id=events[specification["publications"][i]["event_idx"]].id,
                publisher_id=publishers[
                    specification["publications"][i]["publisher_idx"]
                ].id,
            )

    return _generate_models


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,expected_result",
    [
        [
            complete_specification,
            [
                Event(
                    name="event_3",
                    description="desc_3",
                    mobilizon_id="mobid_3",
                    mobilizon_link="moblink_3",
                    thumbnail_link="thumblink_3",
                    location="loc_3",
                    begin_datetime=today + timedelta(days=3),
                    end_datetime=today + timedelta(hours=3),
                )
            ],
        ]
    ],
)
async def test_get_published_events(specification, expected_result, generate_models):
    await generate_models(specification)
    published_events = list(await get_published_events())

    assert len(published_events) == 1
    assert published_events[0].mobilizon_id == expected_result[0].mobilizon_id
    assert (
        published_events[0].begin_datetime.datetime == expected_result[0].begin_datetime
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,expected_result",
    [
        [
            complete_specification,
            [
                Event(
                    name="event_1",
                    description="desc_1",
                    mobilizon_id="mobid_1",
                    mobilizon_link="moblink_1",
                    thumbnail_link="thumblink_1",
                    location="loc_1",
                    begin_datetime=today + timedelta(days=1),
                    end_datetime=today + timedelta(days=1) + timedelta(hours=2),
                ),
            ],
        ]
    ],
)
async def test_get_unpublished_events(specification, expected_result, generate_models):
    await generate_models(specification)
    unpublished_events = list(await get_unpublished_events())

    assert len(unpublished_events) == len(expected_result)

    assert unpublished_events[0].mobilizon_id == expected_result[0].mobilizon_id
    assert unpublished_events[0].begin_datetime == expected_result[0].begin_datetime


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,expected_result",
    [
        [
            complete_specification,
            [
                Event(
                    name="event_1",
                    description="desc_1",
                    mobilizon_id="mobid_1",
                    mobilizon_link="moblink_1",
                    thumbnail_link="thumblink_1",
                    location="loc_1",
                    begin_datetime=today + timedelta(days=1),
                    end_datetime=today + timedelta(days=1) + timedelta(hours=2),
                ),
                Event(
                    name="test event",
                    description="description of the event",
                    mobilizon_id="12345",
                    mobilizon_link="http://some_link.com/123",
                    thumbnail_link="http://some_link.com/123.jpg",
                    location="location",
                    begin_datetime=today + timedelta(days=6),
                    end_datetime=today + timedelta(days=6) + timedelta(hours=2),
                ),
                Event(
                    name="test event",
                    description="description of the event",
                    mobilizon_id="67890",
                    mobilizon_link="http://some_link.com/123",
                    thumbnail_link="http://some_link.com/123.jpg",
                    location="location",
                    begin_datetime=today + timedelta(days=12),
                    end_datetime=today + timedelta(days=12) + timedelta(hours=2),
                ),
            ],
        ]
    ],
)
async def test_create_unpublished_events(
    specification,
    expected_result,
    generate_models,
    event_generator,
):
    await generate_models(specification)

    event_3 = event_generator(begin_date=arrow.get(today + timedelta(days=6)))
    event_4 = event_generator(
        begin_date=arrow.get(today + timedelta(days=12)), mobilizon_id="67890"
    )
    models = await prefetch_event_relations(Event.filter(name="event_1"))

    events_from_internet = [MobilizonEvent.from_model(models[0]), event_3, event_4]

    await create_unpublished_events(
        unpublished_mobilizon_events=events_from_internet,
        active_publishers=["publisher_0", "publisher_1", "publisher_2"],
    )
    unpublished_events = list(await get_unpublished_events())

    assert len(unpublished_events) == 3
    assert unpublished_events[0].mobilizon_id == unpublished_events[0].mobilizon_id
    assert unpublished_events[1].mobilizon_id == unpublished_events[1].mobilizon_id
    assert unpublished_events[2].mobilizon_id == unpublished_events[2].mobilizon_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification",
    [
        complete_specification,
    ],
)
async def test_get_mobilizon_event_publications(specification, generate_models):
    await generate_models(specification)

    models = await prefetch_event_relations(Event.filter(name="event_0"))
    mobilizon_event = MobilizonEvent.from_model(models[0])

    publications = list(await get_mobilizon_event_publications(mobilizon_event))
    for pub in publications:
        await pub.fetch_related("event")
        await pub.fetch_related("publisher")

    assert len(publications) == 2

    assert publications[0].event.name == "event_0"
    assert publications[0].publisher.name == "publisher_0"
    assert publications[0].status == PublicationStatus.WAITING

    assert publications[1].event.name == "event_0"
    assert publications[1].publisher.name == "publisher_1"
    assert publications[1].status == PublicationStatus.COMPLETED
