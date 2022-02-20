import uuid
from logging import DEBUG, INFO

import arrow
import pytest

from mobilizon_reshare.storage.query.converter import event_from_model, event_to_model
from mobilizon_reshare.storage.query.read import get_all_events
from tests.commands.conftest import simple_event_element
from mobilizon_reshare.event.event import EventPublicationStatus
from mobilizon_reshare.main.start import start
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import PublicationStatus


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "elements", [[]],
)
async def test_start_no_event(
    mock_mobilizon_success_answer, mobilizon_answer, caplog, elements
):
    with caplog.at_level(DEBUG):
        assert await start() is None
        assert "No event to publish found" in caplog.text


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "elements",
    [[simple_event_element()], [simple_event_element(), simple_event_element()]],
)
async def test_start_new_event(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    message_collector,
    elements,
):
    with caplog.at_level(DEBUG):
        # calling the start command
        assert await start() is None

        # since the mobilizon_answer contains at least one result, one event to publish must be found and published
        # by the publisher coordinator
        assert "Event to publish found" in caplog.text
        assert message_collector == [
            "test event|Some description",
        ]

        all_events = (
            await Event.all()
            .prefetch_related("publications")
            .prefetch_related("publications__publisher")
        )

        # the start command should save all the events in the database
        assert len(all_events) == len(elements), all_events

        # it should create a publication for each publisher
        publications = all_events[0].publications
        assert len(publications) == 1, publications

        # all the other events should have no publication
        for e in all_events[1:]:
            assert len(e.publications) == 0, e.publications

        # all the publications for the first event should be saved as COMPLETED
        for p in publications[1:]:
            assert p.status == PublicationStatus.COMPLETED

        # the derived status for the event should be COMPLETED
        assert event_from_model(all_events[0]).status == EventPublicationStatus.COMPLETED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.parametrize(
    "elements", [[]],
)
async def test_start_event_from_db(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    message_collector,
    event_generator,
):
    event = event_generator()
    event_model = event_to_model(event)
    await event_model.save()

    with caplog.at_level(DEBUG):
        # calling the start command
        assert await start() is None

        # since the db contains at least one event, this has to be picked and published
        assert "Event to publish found" in caplog.text
        assert message_collector == [
            "test event|description of the event",
        ]

        await event_model.fetch_related("publications", "publications__publisher")
        # it should create a publication for each publisher
        publications = event_model.publications
        assert len(publications) == 1, publications

        # all the publications for the first event should be saved as COMPLETED
        for p in publications:
            assert p.status == PublicationStatus.COMPLETED

        # the derived status for the event should be COMPLETED
        assert event_from_model(event_model).status == EventPublicationStatus.COMPLETED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_invalid_class")]
)
@pytest.mark.parametrize(
    "elements", [[]],
)
async def test_start_publisher_failure(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    message_collector,
    event_generator,
    mock_notifier_config,
):
    event = event_generator()
    event_model = event_to_model(event)
    await event_model.save()

    with caplog.at_level(DEBUG):
        # calling the start command
        assert await start() is None

        # since the db contains at least one event, this has to be picked and published

        await event_model.fetch_related("publications", "publications__publisher")
        # it should create a publication for each publisher
        publications = event_model.publications
        assert len(publications) == 1, publications

        # all the publications for event should be saved as FAILED
        for p in publications:
            assert p.status == PublicationStatus.FAILED
            assert p.reason == "credentials error"

        assert "Event to publish found" in caplog.text
        assert message_collector == [
            f"Publication {p.id} failed with status: 0."
            f"\nReason: credentials error\nPublisher: mock\nEvent: test event"
            for p in publications
            for _ in range(2)
        ]  # 2 publications failed * 2 notifiers
        # the derived status for the event should be FAILED
        assert event_from_model(event_model).status == EventPublicationStatus.FAILED


@pytest.fixture
async def published_event(event_generator):

    event = event_generator()
    event_model = event_to_model(event)
    await event_model.save()
    assert await start() is None
    await event_model.refresh_from_db()
    await event_model.fetch_related("publications")
    for pub in event_model.publications:
        pub.timestamp = arrow.now().shift(days=-2).datetime
        await pub.save()
    return event_model


def second_event_element():
    return {
        "beginsOn": "2021-05-23T12:15:00Z",
        "description": "description of the second event",
        "endsOn": "2021-05-23T15:15:00Z",
        "onlineAddress": None,
        "options": {"showEndTime": True, "showStartTime": True},
        "physicalAddress": None,
        "picture": None,
        "title": "test event",
        "url": "https://some_mobilizon/events/1e2e5943-4a5c-497a-b65d-90457b715d7b",
        "uuid": str(uuid.uuid4()),
        "updatedAt": "2021-05-23T12:15:00Z",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.parametrize(
    "elements", [[second_event_element()]],
)
async def test_start_second_execution(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    message_collector,
    event_generator,
    published_event,
):
    # the fixture published_event provides an existing event in the db

    # I clean the message collector
    message_collector.data = []

    with caplog.at_level(INFO):
        # calling the start command
        assert await start() is None

        # verify that the second event gets published
        assert "Event to publish found" in caplog.text
        assert message_collector == [
            "test event|description of the second event",
        ]
        # I verify that the db event and the new event coming from mobilizon are both in the db
        assert len(list(await get_all_events())) == 2
