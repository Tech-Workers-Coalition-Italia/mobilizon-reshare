from datetime import timedelta
from uuid import UUID

import arrow
import pytest

from mobilizon_reshare.event.event import MobilizonEvent, EventPublicationStatus
from mobilizon_reshare.models.publication import PublicationStatus, Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers.abstract import EventPublication
from mobilizon_reshare.publishers.coordinator import (
    PublisherCoordinatorReport,
    EventPublicationReport,
)
from mobilizon_reshare.publishers.platforms.telegram import (
    TelegramFormatter,
    TelegramPublisher,
)
from mobilizon_reshare.storage.query.read import publications_with_status
from mobilizon_reshare.storage.query.write import (
    save_publication_report,
    update_publishers,
)
from tests.storage import complete_specification
from tests.storage import today

two_publishers_specification = {"publisher": ["telegram", "twitter"]}

event_1 = MobilizonEvent(
    name="event_1",
    description="desc_1",
    mobilizon_id=UUID(int=1),
    mobilizon_link="moblink_1",
    thumbnail_link="thumblink_1",
    location="loc_1",
    status=EventPublicationStatus.WAITING,
    begin_datetime=arrow.get(today + timedelta(days=1)),
    end_datetime=arrow.get(today + timedelta(days=1) + timedelta(hours=2)),
)


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
    specification,
    names,
    expected_result,
    generate_models,
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
    specification,
    report,
    event,
    expected_result,
    generate_models,
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
