from uuid import UUID

import pytest

from mobilizon_reshare.storage.query.read_query import (
    get_unpublished_events,
    get_all_events,
)


@pytest.mark.parametrize(
    "spec, expected_output_len",
    [
        [{"event": 2, "publisher": [], "publications": []}, 2],
        [{"event": 0, "publisher": [], "publications": []}, 0],
        [
            {
                "event": 2,
                "publisher": ["zulip"],
                "publications": [{"event_idx": 0, "publisher_idx": 0}],
            },
            1,
        ],
    ],
)
@pytest.mark.asyncio
async def test_get_unpublished_events_db_only(
    spec, generate_models, expected_output_len, event_generator
):
    """Testing that with no events on Mobilizon, I retrieve all the DB unpublished events """
    await generate_models(spec)
    unpublished_events = await get_unpublished_events([])
    assert len(unpublished_events) == expected_output_len


@pytest.mark.parametrize("num_mobilizon_events", [0, 2])
@pytest.mark.asyncio
async def test_get_unpublished_events_mobilizon_only_no_publications(
    event_generator, num_mobilizon_events
):
    """Testing that when there are no events present in the DB, all the mobilizon events are returned"""
    mobilizon_events = [
        event_generator(mobilizon_id=UUID(int=i), published=False)
        for i in range(num_mobilizon_events)
    ]
    unpublished_events = await get_unpublished_events(mobilizon_events)
    assert unpublished_events == mobilizon_events


@pytest.mark.asyncio
async def test_get_unpublished_events_no_overlap(event_generator):
    "Testing that all the events are returned when there's no overlap"
    all_events = [
        event_generator(mobilizon_id=UUID(int=i), published=False) for i in range(4)
    ]
    db_events = all_events[:1]
    mobilizon_events = all_events[1:]
    for e in db_events:
        await e.to_model().save()

    unpublished_events = await get_unpublished_events(mobilizon_events)
    assert sorted(all_events, key=lambda x: x.mobilizon_id) == sorted(
        unpublished_events, key=lambda x: x.mobilizon_id
    )


@pytest.mark.asyncio
async def test_get_unpublished_events_overlap(event_generator):
    """Testing that there are no duplicates when an event from mobilizon is already present in the db
    and that no event is lost"""

    all_events = [
        event_generator(mobilizon_id=UUID(int=i), published=False) for i in range(4)
    ]
    db_events = all_events[:2]
    mobilizon_events = all_events[1:]
    for e in db_events:
        await e.to_model().save()

    unpublished_events = await get_unpublished_events(mobilizon_events)
    assert len(unpublished_events) == 4


@pytest.mark.asyncio
async def test_get_all_events(event_generator):
    all_events = [
        event_generator(mobilizon_id=UUID(int=i), published=False) for i in range(4)
    ]
    for e in all_events:
        await e.to_model().save()

    assert list(await get_all_events()) == all_events
