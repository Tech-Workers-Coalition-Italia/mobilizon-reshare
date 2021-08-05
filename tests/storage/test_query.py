from datetime import timedelta
from uuid import UUID

import arrow
import pytest

from mobilizon_bots.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import PublicationStatus, Publication
from mobilizon_bots.models.publisher import Publisher
from mobilizon_bots.publishers.coordinator import (
    PublisherCoordinatorReport,
    PublicationReport,
)
from mobilizon_bots.storage.query import (
    get_published_events,
    get_unpublished_events,
    create_unpublished_events,
    get_mobilizon_event_publications,
    prefetch_event_relations,
    get_publishers,
    publications_with_status,
    update_publishers,
    save_publication_report,
)
from tests.storage import today

two_publishers_specification = {"publisher": 2}

complete_specification = {
    "event": 4,
    "publications": [
        {"event_idx": 0, "publisher_idx": 0},
        {"event_idx": 0, "publisher_idx": 1, "status": PublicationStatus.COMPLETED},
        {"event_idx": 1, "publisher_idx": 0, "status": PublicationStatus.WAITING},
        {"event_idx": 1, "publisher_idx": 1},
        {"event_idx": 2, "publisher_idx": 2, "status": PublicationStatus.FAILED},
        {"event_idx": 2, "publisher_idx": 1, "status": PublicationStatus.COMPLETED},
        {"event_idx": 3, "publisher_idx": 2, "status": PublicationStatus.COMPLETED},
    ],
}


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
                    publication_time={
                        "publisher_2": arrow.get(today + timedelta(hours=6)),
                    },
                    status=EventPublicationStatus.COMPLETED,
                    begin_datetime=arrow.get(today + timedelta(days=3)),
                    end_datetime=arrow.get(
                        today + timedelta(days=3) + timedelta(hours=2)
                    ),
                )
            ],
        ]
    ],
)
async def test_get_published_events(specification, expected_result, generate_models):
    await generate_models(specification)
    published_events = list(await get_published_events())

    assert len(published_events) == len(expected_result)
    assert published_events == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,expected_result",
    [
        [
            complete_specification,
            [
                MobilizonEvent(
                    name="event_1",
                    description="desc_1",
                    mobilizon_id="mobid_1",
                    mobilizon_link="moblink_1",
                    thumbnail_link="thumblink_1",
                    location="loc_1",
                    status=EventPublicationStatus.WAITING,
                    begin_datetime=arrow.get(today + timedelta(days=1)),
                    end_datetime=arrow.get(
                        today + timedelta(days=1) + timedelta(hours=2)
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
    specification, expected_result, generate_models, event_generator,
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
    "specification", [complete_specification],
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
                Publication(
                    id=UUID(int=0),
                    status=PublicationStatus.WAITING,
                    timestamp=today + timedelta(hours=0),
                    event_id=UUID(int=0),
                    publisher_id=UUID(int=0),
                ),
                Publication(
                    id=UUID(int=2),
                    status=PublicationStatus.WAITING,
                    timestamp=today + timedelta(hours=2),
                    event_id=UUID(int=0),
                    publisher_id=UUID(int=1),
                ),
                Publication(
                    id=UUID(int=3),
                    status=PublicationStatus.WAITING,
                    timestamp=today + timedelta(hours=3),
                    event_id=UUID(int=1),
                    publisher_id=UUID(int=1),
                ),
            ],
        ],
        [
            PublicationStatus.WAITING,
            "mobid_1",
            None,
            None,
            [
                Publication(
                    id=UUID(int=2),
                    status=PublicationStatus.COMPLETED,
                    timestamp=today + timedelta(hours=2),
                    event_id=UUID(int=1),
                    publisher_id=UUID(int=1),
                ),
                Publication(
                    id=UUID(int=3),
                    status=PublicationStatus.WAITING,
                    timestamp=today + timedelta(hours=5),
                    event_id=UUID(int=1),
                    publisher_id=UUID(int=1),
                ),
            ],
        ],
        [
            PublicationStatus.WAITING,
            None,
            arrow.get(today + timedelta(hours=-1)),
            arrow.get(today + timedelta(hours=1)),
            [
                Publication(
                    id=UUID(int=0),
                    status=PublicationStatus.WAITING,
                    timestamp=today + timedelta(hours=0),
                    event_id=UUID(int=0),
                    publisher_id=UUID(int=0),
                ),
            ],
        ],
        [
            PublicationStatus.WAITING,
            None,
            arrow.get(today + timedelta(hours=1)),
            None,
            [
                Publication(
                    id=UUID(int=2),
                    status=PublicationStatus.WAITING,
                    timestamp=today + timedelta(hours=2),
                    event_id=UUID(int=0),
                    publisher_id=UUID(int=1),
                ),
                Publication(
                    id=UUID(int=3),
                    status=PublicationStatus.WAITING,
                    timestamp=today + timedelta(hours=5),
                    event_id=UUID(int=1),
                    publisher_id=UUID(int=1),
                ),
            ],
        ],
        [
            PublicationStatus.WAITING,
            None,
            None,
            arrow.get(today + timedelta(hours=1)),
            [
                Publication(
                    id=UUID(int=0),
                    status=PublicationStatus.WAITING,
                    timestamp=today + timedelta(hours=0),
                    event_id=UUID(int=0),
                    publisher_id=UUID(int=0),
                ),
            ],
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

    assert len(publications) == len(expected_result)
    assert publications == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,names,expected_result",
    [
        [
            two_publishers_specification,
            ["publisher_0", "publisher_1"],
            {
                Publisher(id=UUID(int=0), name="publisher_0"),
                Publisher(id=UUID(int=1), name="publisher_1"),
            },
        ],
        [
            {"publisher": 0},
            ["publisher_0", "publisher_1"],
            {"publisher_0", "publisher_1"},
        ],
        [
            two_publishers_specification,
            ["publisher_0", "publisher_2", "publisher_3"],
            {"publisher_0", "publisher_1", "publisher_2", "publisher_3"},
        ],
    ],
)
async def test_update_publishers(
    specification, names, expected_result, generate_models,
):
    await generate_models(specification)
    await update_publishers(names)
    if type(list(expected_result)[0]) == Publisher:
        publishers = set(await get_publishers())
    else:
        publishers = set(p.name for p in await get_publishers())

    assert len(publishers) == len(expected_result)
    assert publishers == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,report,event,expected_result",
    [
        [
            complete_specification,
            PublisherCoordinatorReport(
                reports={
                    UUID(int=2): PublicationReport(
                        status=PublicationStatus.FAILED, reason="Invalid credentials"
                    ),
                    UUID(int=3): PublicationReport(
                        status=PublicationStatus.COMPLETED, reason=""
                    ),
                }
            ),
            MobilizonEvent(
                name="event_1",
                description="desc_1",
                mobilizon_id="mobid_1",
                mobilizon_link="moblink_1",
                thumbnail_link="thumblink_1",
                location="loc_1",
                status=EventPublicationStatus.WAITING,
                begin_datetime=arrow.get(today + timedelta(days=1)),
                end_datetime=arrow.get(today + timedelta(days=1) + timedelta(hours=2)),
            ),
            {
                UUID(int=2): Publication(
                    id=UUID(int=2),
                    status=PublicationStatus.FAILED,
                    reason="Invalid credentials",
                ),
                UUID(int=3): Publication(
                    id=UUID(int=0), status=PublicationStatus.COMPLETED, reason=""
                ),
            },
        ],
    ],
)
async def test_save_publication_report(
    specification, report, event, expected_result, generate_models,
):
    await generate_models(specification)
    await save_publication_report(report, event)
    publication_ids = set(report.reports.keys())
    publications = {
        p_id: await Publication.filter(id=p_id).first() for p_id in publication_ids
    }

    assert len(publications) == len(expected_result)
    for i in publication_ids:
        assert publications[i].status == expected_result[i].status
        assert publications[i].reason == expected_result[i].reason
        assert publications[i].timestamp
