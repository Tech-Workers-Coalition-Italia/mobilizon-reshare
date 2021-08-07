from datetime import timedelta

import arrow
import pytest

from mobilizon_bots.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import PublicationStatus
from mobilizon_bots.storage.query import events_with_status
from mobilizon_bots.storage.query import (
    get_published_events,
    get_unpublished_events,
    create_unpublished_events,
    get_mobilizon_event_publications,
    prefetch_event_relations,
    get_publishers,
    publications_with_status,
)
from tests.storage import result_publication
from tests.storage import complete_specification
from tests.storage import today

event_0 = MobilizonEvent(
    name="event_0",
    description="desc_0",
    mobilizon_id="mobid_0",
    mobilizon_link="moblink_0",
    thumbnail_link="thumblink_0",
    location="loc_0",
    publication_time={
        "publisher_0": arrow.get(today + timedelta(hours=0)),
        "publisher_1": arrow.get(today + timedelta(hours=1)),
        "publisher_2": arrow.get(today + timedelta(hours=2)),
    },
    status=EventPublicationStatus.COMPLETED,
    begin_datetime=arrow.get(today + timedelta(days=0)),
    end_datetime=arrow.get(today + timedelta(days=0) + timedelta(hours=2)),
)


@pytest.mark.asyncio
async def test_get_published_events(generate_models):
    await generate_models(complete_specification)
    published_events = list(await get_published_events())

    assert len(published_events) == 1
    assert published_events == [event_0]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,expected_result",
    [
        [
            complete_specification,
            [
                MobilizonEvent(
                    name="event_3",
                    description="desc_3",
                    mobilizon_id="mobid_3",
                    mobilizon_link="moblink_3",
                    thumbnail_link="thumblink_3",
                    location="loc_3",
                    status=EventPublicationStatus.WAITING,
                    begin_datetime=arrow.get(today + timedelta(days=3)),
                    end_datetime=arrow.get(
                        today + timedelta(days=3) + timedelta(hours=2)
                    ),
                ),
            ],
        ]
    ],
)
async def test_get_unpublished_events(specification, expected_result, generate_models):
    await generate_models(specification)
    unpublished_events = list(await get_unpublished_events())

    assert len(unpublished_events) == len(expected_result)
    assert unpublished_events == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected_result",
    [
        [
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
    expected_result, generate_models, event_generator,
):
    await generate_models(complete_specification)

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

    assert len(unpublished_events) == 4


@pytest.mark.asyncio
async def test_get_mobilizon_event_publications(generate_models):
    await generate_models(complete_specification)

    models = await prefetch_event_relations(Event.filter(name="event_0"))
    mobilizon_event = MobilizonEvent.from_model(models[0])

    publications = list(await get_mobilizon_event_publications(mobilizon_event))
    for pub in publications:
        await pub.fetch_related("event")
        await pub.fetch_related("publisher")

    assert len(publications) == 3

    assert publications[0].event.name == "event_0"
    assert publications[0].publisher.name == "publisher_0"
    assert publications[0].status == PublicationStatus.COMPLETED

    assert publications[1].event.name == "event_0"
    assert publications[1].publisher.name == "publisher_1"
    assert publications[1].status == PublicationStatus.COMPLETED

    assert publications[2].event.name == "event_0"
    assert publications[2].publisher.name == "publisher_2"
    assert publications[2].status == PublicationStatus.COMPLETED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name,expected_result",
    [
        [None, {"publisher_0", "publisher_1", "publisher_2"}],
        ["publisher_0", {"publisher_0"}],
    ],
)
async def test_get_publishers(
    name, expected_result, generate_models,
):
    await generate_models(complete_specification)
    result = await get_publishers(name)

    if type(result) == list:
        publishers = set(p.name for p in result)
    else:
        publishers = {result.name}

    assert len(publishers) == len(expected_result)
    assert publishers == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,mobilizon_id,from_date,to_date,expected_result",
    [
        [
            PublicationStatus.WAITING,
            None,
            None,
            None,
            [
                result_publication[3],
                result_publication[4],
                result_publication[8],
                result_publication[9],
                result_publication[10],
                result_publication[11],
            ],
        ],
        [
            PublicationStatus.WAITING,
            "mobid_1",
            None,
            None,
            [result_publication[3], result_publication[4]],
        ],
        [
            PublicationStatus.WAITING,
            None,
            arrow.get(today),
            arrow.get(today + timedelta(hours=6)),
            [result_publication[3], result_publication[4]],
        ],
        [
            PublicationStatus.COMPLETED,
            None,
            arrow.get(today + timedelta(hours=1)),
            None,
            [result_publication[2], result_publication[5], result_publication[7]],
        ],
        [
            PublicationStatus.COMPLETED,
            None,
            None,
            arrow.get(today + timedelta(hours=2)),
            [result_publication[0], result_publication[1]],
        ],
    ],
)
async def test_publications_with_status(
    status, mobilizon_id, from_date, to_date, expected_result, generate_models,
):
    await generate_models(complete_specification)
    publications = await publications_with_status(
        status=status,
        event_mobilizon_id=mobilizon_id,
        from_date=from_date,
        to_date=to_date,
    )

    assert publications == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, expected_events_count",
    [
        (EventPublicationStatus.COMPLETED, 1),
        (EventPublicationStatus.FAILED, 1),
        (EventPublicationStatus.PARTIAL, 1),
        (EventPublicationStatus.WAITING, 1),
    ],
)
async def test_event_with_status(generate_models, status, expected_events_count):
    await generate_models(complete_specification)
    result = list(await events_with_status([status]))

    assert len(result) == expected_events_count
