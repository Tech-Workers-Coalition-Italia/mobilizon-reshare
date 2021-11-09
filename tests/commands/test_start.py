from logging import DEBUG

import pytest

from tests.commands.conftest import simple_event_element
from mobilizon_reshare.event.event import MobilizonEvent, EventPublicationStatus
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
@pytest.mark.parametrize("publication_window", [(0, 24)])
async def test_start_new_event(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    mock_publication_window,
    message_collector,
):
    with caplog.at_level(DEBUG):
        # calling the start command
        assert await start() is None

        # since the mobilizon_answer contains at least one result, one event to publish must be found and published
        # by the publisher coordinator
        assert "Event to publish found" in caplog.text
        assert message_collector == [
            "test event|Some description",
            "test event|Some description",
        ]

        all_events = (
            await Event.all()
            .prefetch_related("publications")
            .prefetch_related("publications__publisher")
        )

        # the start command should save all the events in the database
        assert len(all_events) == len(
            mobilizon_answer["data"]["group"]["organizedEvents"]["elements"]
        ), all_events

        # it should create a publication for each publisher
        publications = all_events[0].publications
        assert len(publications) == 2, publications

        # all the other events should have no publication
        for e in all_events[1:]:
            assert len(e.publications) == 0, e.publications

        # all the publications for the first event should be saved as COMPLETED
        for p in publications[1:]:
            assert p.status == PublicationStatus.COMPLETED

        # the derived status for the event should be COMPLETED
        assert (
            MobilizonEvent.from_model(all_events[0]).status
            == EventPublicationStatus.COMPLETED
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.parametrize(
    "elements", [[]],
)
@pytest.mark.parametrize("publication_window", [(0, 24)])
async def test_start_event_from_db(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    mock_publication_window,
    message_collector,
    event_generator,
):
    event = event_generator()
    event_model = event.to_model()
    await event_model.save()

    with caplog.at_level(DEBUG):
        # calling the start command
        assert await start() is None

        # since the db contains at least one event, this has to be picked and published
        assert "Event to publish found" in caplog.text
        assert message_collector == [
            "test event|description of the event",
            "test event|description of the event",
        ]

        await event_model.fetch_related("publications", "publications__publisher")
        # it should create a publication for each publisher
        publications = event_model.publications
        assert len(publications) == 2, publications

        # all the publications for the first event should be saved as COMPLETED
        for p in publications[1:]:
            assert p.status == PublicationStatus.COMPLETED

        # the derived status for the event should be COMPLETED
        assert (
            MobilizonEvent.from_model(event_model).status
            == EventPublicationStatus.COMPLETED
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_invalid_class")]
)
@pytest.mark.parametrize(
    "elements", [[]],
)
@pytest.mark.parametrize("publication_window", [(0, 24)])
async def test_start_publisher_failure(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    mock_publication_window,
    message_collector,
    event_generator,
    mock_notifier_config,
):
    event = event_generator()
    event_model = event.to_model()
    await event_model.save()

    with caplog.at_level(DEBUG):
        # calling the start command
        assert await start() is None

        # since the db contains at least one event, this has to be picked and published

        await event_model.fetch_related("publications", "publications__publisher")
        # it should create a publication for each publisher
        publications = event_model.publications
        assert len(publications) == 2, publications

        # all the publications for event should be saved as FAILED
        for p in publications:
            assert p.status == PublicationStatus.FAILED
            assert p.reason == "credentials error"

        assert "Event to publish found" in caplog.text
        assert message_collector == [
            f"Publication {p.id} failed with status: 1."
            f"\nReason: credentials error\nPublisher: mock"
            for p in publications
            for _ in range(2)
        ]  # 2 publications failed * 2 notifiers
        # the derived status for the event should be FAILED
        assert (
            MobilizonEvent.from_model(event_model).status
            == EventPublicationStatus.FAILED
        )
