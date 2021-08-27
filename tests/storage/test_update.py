from datetime import timedelta
from uuid import UUID

import arrow
import pytest

from mobilizon_reshare.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_reshare.models.publication import PublicationStatus, Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.coordinator import (
    PublisherCoordinatorReport,
    PublicationReport,
)
from mobilizon_reshare.storage.query import (
    get_publishers,
    update_publishers,
    save_publication_report,
)
from mobilizon_reshare.storage.query import publications_with_status
from tests.storage import complete_specification
from tests.storage import today

two_publishers_specification = {"publisher": ["telegram", "twitter"]}


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
                    UUID(int=3): PublicationReport(
                        status=PublicationStatus.FAILED,
                        reason="Invalid credentials",
                        publication_id=UUID(int=3),
                    ),
                    UUID(int=4): PublicationReport(
                        status=PublicationStatus.COMPLETED,
                        reason="",
                        publication_id=UUID(int=4),
                    ),
                },
                publishers={},
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
                UUID(int=3): Publication(
                    id=UUID(int=3),
                    status=PublicationStatus.FAILED,
                    reason="Invalid credentials",
                ),
                UUID(int=4): Publication(
                    id=UUID(int=4), status=PublicationStatus.COMPLETED, reason=""
                ),
            },
        ],
    ],
)
async def test_save_publication_report(
    specification, report, event, expected_result, generate_models,
):
    await generate_models(specification)

    publications = await publications_with_status(
        status=PublicationStatus.WAITING, event_mobilizon_id=event.mobilizon_id,
    )
    await save_publication_report(report, publications)
    publication_ids = set(report.reports.keys())
    publications = {
        p_id: await Publication.filter(id=p_id).first() for p_id in publication_ids
    }

    assert len(publications) == len(expected_result)
    for i in publication_ids:
        assert publications[i].status == expected_result[i].status
        assert publications[i].reason == expected_result[i].reason
        assert publications[i].timestamp
