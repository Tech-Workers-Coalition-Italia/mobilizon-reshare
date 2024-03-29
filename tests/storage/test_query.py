from datetime import timedelta

import arrow
import pytest

from mobilizon_reshare.dataclasses.event import (
    _EventPublicationStatus,
    get_published_events,
    get_mobilizon_events_with_status,
    get_mobilizon_events_without_publications,
)
from mobilizon_reshare.storage.query.read import (
    get_all_events,
    get_event,
)
from mobilizon_reshare.dataclasses.publication import build_publications_for_event
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.storage.query.read import publications_with_status
from tests import today
from tests.commands.test_publish import one_unpublished_event_specification
from tests.conftest import event_0, event_1, event_3
from tests.storage import complete_specification
from tests.storage import result_publication


@pytest.mark.asyncio
async def test_get_published_events(generate_models):
    await generate_models(complete_specification)
    published_events = list(await get_published_events())

    assert len(published_events) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,mobilizon_id,from_date,to_date,expected_result",
    [
        [
            PublicationStatus.COMPLETED,
            None,
            arrow.get(today + timedelta(hours=1)),
            None,
            [result_publication[2], result_publication[4], result_publication[5]],
        ],
        [
            PublicationStatus.COMPLETED,
            None,
            None,
            arrow.get(today + timedelta(hours=2)),
            [result_publication[0], result_publication[1]],
        ],
        [
            PublicationStatus.FAILED,
            None,
            None,
            arrow.get(today + timedelta(hours=5)),
            [result_publication[3]],
        ],
    ],
)
async def test_publications_with_status(
    status, mobilizon_id, from_date, to_date, expected_result, generate_models,
):
    await generate_models(complete_specification)
    publications = await publications_with_status(
        status=status, from_date=from_date, to_date=to_date,
    )

    assert publications == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, expected_events_count",
    [(_EventPublicationStatus.COMPLETED, 2), (_EventPublicationStatus.PARTIAL, 1)],
)
async def test_event_with_status(generate_models, status, expected_events_count):
    await generate_models(complete_specification)
    result = list(await get_mobilizon_events_with_status([status]))

    assert len(result) == expected_events_count


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, expected_events_count, begin_window, end_window",
    [
        (
            _EventPublicationStatus.COMPLETED,
            2,
            arrow.get(today + timedelta(hours=-1)),
            None,
        ),
        (
            _EventPublicationStatus.COMPLETED,
            1,
            arrow.get(today + timedelta(hours=1)),
            None,
        ),
        (
            _EventPublicationStatus.COMPLETED,
            1,
            arrow.get(today + timedelta(hours=-2)),
            arrow.get(today + timedelta(hours=1)),
        ),
        (
            _EventPublicationStatus.COMPLETED,
            0,
            arrow.get(today + timedelta(hours=-2)),
            arrow.get(today + timedelta(hours=0)),
        ),
    ],
)
async def test_event_with_status_window(
    generate_models, status, expected_events_count, begin_window, end_window
):
    await generate_models(complete_specification)
    result = list(
        await get_mobilizon_events_with_status(
            [status], from_date=begin_window, to_date=end_window
        )
    )

    assert len(result) == expected_events_count


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec, expected_events",
    [
        ({"event": 2, "publications": [], "publisher": ["zulip"]}, [event_0, event_1],),
        (
            {
                "event": 3,
                "publications": [
                    {
                        "event_idx": 1,
                        "publisher_idx": 0,
                        "status": PublicationStatus.FAILED,
                    },
                    {
                        "event_idx": 2,
                        "publisher_idx": 0,
                        "status": PublicationStatus.COMPLETED,
                    },
                ],
                "publisher": ["zulip"],
            },
            [event_0],
        ),
        (complete_specification, [event_3],),
    ],
)
async def test_events_without_publications(spec, expected_events, generate_models):
    await generate_models(spec)
    unpublished_events = list(await get_mobilizon_events_without_publications())
    assert len(unpublished_events) == len(expected_events)
    assert unpublished_events == expected_events


@pytest.mark.asyncio
async def test_get_all_events(generate_models):
    await generate_models(one_unpublished_event_specification)

    all_events = [await get_event(event_0.mobilizon_id)]
    assert list(await get_all_events()) == all_events


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_active_publishers, spec, event, n_publications",
    [
        ([], {"event": 2, "publications": [], "publisher": ["zulip"]}, event_0, 0,),
        (
            ["zulip"],
            {"event": 2, "publications": [], "publisher": ["zulip"]},
            event_0,
            1,
        ),
        (
            ["telegram", "zulip", "mastodon", "facebook"],
            {
                "event": 2,
                "publications": [],
                "publisher": ["telegram", "zulip", "mastodon", "facebook"],
            },
            event_0,
            4,
        ),
    ],
    indirect=["mock_active_publishers"],
)
async def test_build_publications(
    mock_active_publishers, spec, event, n_publications, generate_models
):
    await generate_models(spec)

    publications = list(
        await build_publications_for_event(event, mock_active_publishers)
    )

    assert len(publications) == n_publications

    for p in publications:
        assert p.event == event
        assert p.publisher.name in mock_active_publishers
