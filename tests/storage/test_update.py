from uuid import UUID

import pytest

from mobilizon_reshare.models.publication import PublicationStatus, Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.dataclasses.publication import EventPublication
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    EventPublicationReport,
    PublisherCoordinatorReport,
)
from mobilizon_reshare.publishers.platforms.telegram import (
    TelegramFormatter,
    TelegramPublisher,
)
from mobilizon_reshare.storage.query.write import (
    save_publication_report,
    update_publishers,
    create_unpublished_events,
)
from tests.storage import complete_specification
from tests.conftest import event_6, event_0, event_1, event_2, event_3, event_3_updated

two_publishers_specification = {"publisher": ["telegram", "twitter"]}

all_published_specification = {
    "event": 2,
    "publications": [
        {"event_idx": 0, "publisher_idx": 1, "status": PublicationStatus.FAILED},
        {"event_idx": 1, "publisher_idx": 0, "status": PublicationStatus.COMPLETED},
    ],
    "publisher": ["telegram", "twitter"],
}

two_events_specification = {
    "event": 2,
    "publications": [
        {"event_idx": 0, "publisher_idx": 1, "status": PublicationStatus.FAILED},
    ],
    "publisher": ["telegram", "twitter"],
}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,names,expected_result",
    [
        [
            two_publishers_specification,
            ["telegram", "twitter"],
            {
                Publisher(id=UUID(int=0), name="telegram"),
                Publisher(id=UUID(int=1), name="twitter"),
            },
        ],
        [
            {"publisher": ["telegram"]},
            ["telegram", "twitter"],
            {"telegram", "twitter"},
        ],
        [
            two_publishers_specification,
            ["telegram", "mastodon", "facebook"],
            {"telegram", "twitter", "mastodon", "facebook"},
        ],
    ],
)
async def test_update_publishers(
    specification, names, expected_result, generate_models,
):
    await generate_models(specification)
    await update_publishers(names)
    if type(list(expected_result)[0]) == Publisher:
        publishers = set(await Publisher.all())
    else:
        publishers = set(p.name for p in await Publisher.all())

    assert len(publishers) == len(expected_result)
    assert publishers == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,events_from_mobilizon,expected_result",
    [
        [
            # Empty DB
            {"event": 0, "publications": [], "publisher": []},
            [event_1],
            [event_1],
        ],
        [
            # Test whether the query actually does nothing when all events are published
            all_published_specification,
            [event_1],
            [],
        ],
        [
            # Test whether the query actually returns only unknown unpublished events
            all_published_specification,
            [event_2],
            [event_2],
        ],
        [
            # Test whether the query actually merges remote and local state
            {"event": 2, "publisher": ["telegram", "mastodon", "facebook"]},
            [event_2],
            [event_0, event_1, event_2],
        ],
        [
            # Test whether the query actually merges remote and local state
            complete_specification,
            [event_0, event_1, event_2, event_6],
            [event_3, event_6],
        ],
        [
            # Test update
            complete_specification,
            [event_0, event_3_updated, event_6],
            [event_3_updated, event_6],
        ],
    ],
)
async def test_create_unpublished_events(
    specification, events_from_mobilizon, expected_result, generate_models,
):
    await generate_models(specification)

    unpublished_events = await create_unpublished_events(events_from_mobilizon)

    assert len(unpublished_events) == len(expected_result)
    assert unpublished_events == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,report,event,expected_result",
    [
        [
            complete_specification,
            PublisherCoordinatorReport(
                publications=[],
                reports=[
                    EventPublicationReport(
                        status=PublicationStatus.COMPLETED,
                        reason="",
                        publication=EventPublication(
                            id=UUID(int=6),
                            formatter=TelegramFormatter(),
                            event=event_1,
                            publisher=TelegramPublisher(),
                        ),
                    ),
                ],
            ),
            event_1,
            {
                UUID(int=6): Publication(
                    id=UUID(int=6), status=PublicationStatus.COMPLETED, reason=""
                ),
            },
        ],
    ],
)
async def test_save_publication_report(
    specification, report, event, expected_result, generate_models,
):
    await generate_models(specification)
    known_publication_ids = set(p.id for p in await Publication.all())

    await save_publication_report(report)

    publications = {
        p.id: p for p in await Publication.filter(id__not_in=known_publication_ids)
    }

    assert len(publications) == len(expected_result)
    for i in publications.keys():
        assert publications[i].status == expected_result[i].status
        assert publications[i].reason == expected_result[i].reason
        assert publications[i].timestamp
