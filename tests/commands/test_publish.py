from logging import DEBUG

import pytest

from mobilizon_reshare.main.publish import select_and_publish, publish_event
from mobilizon_reshare.event.event import EventPublicationStatus, MobilizonEvent
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.storage.query.read import get_all_publications
from tests.conftest import event_0, event_1

one_unpublished_event_specification = {
    "event": 1,
    "publisher": ["telegram", "twitter", "mastodon", "zulip"],
}
three_event_specification = {
    "event": 3,
    "publications": [
        {"event_idx": 0, "publisher_idx": 0, "status": PublicationStatus.COMPLETED}
    ],
    "publisher": ["telegram", "twitter", "mastodon", "zulip"],
}


@pytest.mark.asyncio
async def test_publish_no_event(caplog, command_config):
    with caplog.at_level(DEBUG):
        assert await select_and_publish(command_config) is None
        assert "No event to publish found" in caplog.text


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "specification,expected_event",
    [
        [one_unpublished_event_specification, event_0],
        [three_event_specification, event_1],
    ],
)
async def test_select_and_publish_new_event(
    generate_models,
    caplog,
    mock_publisher_config,
    message_collector,
    specification,
    expected_event,
    command_config,
):
    await generate_models(specification)
    with caplog.at_level(DEBUG):
        # calling the publish command without arguments
        assert await select_and_publish(command_config) is not None

        assert "Event to publish found" in caplog.text
        assert message_collector == [
            f"{expected_event.name}|{expected_event.description}",
        ]

        event = (
            await Event.filter(mobilizon_id=expected_event.mobilizon_id)
            .prefetch_related("publications")
            .prefetch_related("publications__publisher")
        )[0]

        # it should create a publication for each publisher
        publications = event.publications
        assert len(publications) == 1, publications

        # all the publications for the first event should be saved as COMPLETED
        for p in publications:
            assert p.status == PublicationStatus.COMPLETED

        # the derived status for the event should be COMPLETED
        assert (
            MobilizonEvent.from_model(event).status == EventPublicationStatus.COMPLETED
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class,publishers,expected",
    [
        [pytest.lazy_fixture("mock_publisher_class"), None, {"mock"}],
        [pytest.lazy_fixture("mock_publisher_class"), [], {"mock"}],
        [pytest.lazy_fixture("mock_publisher_class"), [None, None], {"mock"}],
        [pytest.lazy_fixture("mock_zulip_publisher_class"), ["zulip"], {"zulip"}],
    ],
)
async def test_publish_event(
    generate_models,
    caplog,
    mock_publisher_config,
    message_collector,
    publishers,
    expected,
    command_config,
):
    await generate_models(one_unpublished_event_specification)
    with caplog.at_level(DEBUG):
        # calling mobilizon-reshare publish -E <UUID> -p <platform>
        report = await publish_event(event_0, command_config, publishers)
        assert report is not None
        assert report.successful

        # We test whether we published only to the expected platforms
        assert {pub.publication.publisher.name for pub in report.reports} == expected
        publications = list(await get_all_publications())
        assert len(publications) == len(expected)
        assert all(p.status == PublicationStatus.COMPLETED for p in publications)
        assert {p.publisher.name for p in publications} == expected
