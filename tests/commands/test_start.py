from logging import DEBUG, INFO

import pytest

from mobilizon_reshare.config.command import CommandConfig
from mobilizon_reshare.storage.query.read import get_all_mobilizon_events
from tests.commands.conftest import simple_event_element, second_event_element
from mobilizon_reshare.event.event import EventPublicationStatus, MobilizonEvent
from mobilizon_reshare.main.start import start
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import PublicationStatus

one_published_event_specification = {
    "event": 1,
    "publications": [
        {"event_idx": 0, "publisher_idx": 0, "status": PublicationStatus.COMPLETED}
    ],
    "publisher": ["telegram", "twitter", "mastodon", "zulip"],
}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dry_run", [True, False]
)  # the behavior should be identical with and without dry-run
@pytest.mark.parametrize(
    "elements", [[]],
)
async def test_start_no_event(
    mock_mobilizon_success_answer, mobilizon_answer, caplog, elements, dry_run
):
    with caplog.at_level(DEBUG):
        assert await start(CommandConfig(dry_run=dry_run)) is None
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
    command_config,
):
    with caplog.at_level(DEBUG):
        # calling the start command
        assert await start(command_config) is not None

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
async def test_start_event_from_db(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    message_collector,
    event_generator,
    command_config,
):
    event = event_generator()
    event_model = event.to_model()
    await event_model.save()

    with caplog.at_level(DEBUG):
        # calling the start command
        result = await start(command_config)

        assert result.successful
        assert len(result.reports) == 1
        assert (
            result.reports[0].published_content == "test event|description of the event"
        )

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
async def test_start_publisher_failure(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    message_collector,
    event_generator,
    mock_notifier_config,
    command_config,
):
    event = event_generator()
    event_model = event.to_model()
    await event_model.save()

    with caplog.at_level(DEBUG):
        # calling the start command
        result = await start(command_config)

        assert not result.successful
        assert len(result.reports) == 1
        assert result.reports[0].published_content is None

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
        assert (
            MobilizonEvent.from_model(event_model).status
            == EventPublicationStatus.FAILED
        )


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
    generate_models,
    command_config,
):
    await generate_models(one_published_event_specification)

    # I clean the message collector
    message_collector.data = []

    with caplog.at_level(INFO):
        # calling the start command
        assert await start(command_config) is not None

        # verify that the second event gets published
        assert "Event to publish found" in caplog.text
        assert message_collector == [
            "event_1|desc_1",
        ]
        # I verify that the db event and the new event coming from mobilizon are both in the db
        assert len(list(await get_all_mobilizon_events())) == 2


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "elements",
    [[simple_event_element()], [simple_event_element(), simple_event_element()]],
)
async def test_start_dry_run(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    message_collector,
    elements,
):
    with caplog.at_level(DEBUG):
        # calling the start command
        result = await start(CommandConfig(dry_run=True))
        assert result.successful
        assert len(result.reports) == 1
        assert result.reports[0].published_content == "test event|Some description"

        assert "Event to publish found" in caplog.text
        assert (
            "Executing in dry run mode. No event is going to be published."
            in caplog.text
        )
        assert (
            message_collector == []
        )  # the configured publisher shouldn't be called if in dry run mode

        all_events = (
            await Event.all()
            .prefetch_related("publications")
            .prefetch_related("publications__publisher")
        )

        # the start command should save all the events in the database
        assert len(all_events) == len(elements), all_events

        # it should create no publication
        publications = all_events[0].publications
        assert len(publications) == 0, publications


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "elements",
    [[simple_event_element()], [simple_event_element(), simple_event_element()]],
)
async def test_start_dry_run_second_execution(
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    mock_publisher_config,
    message_collector,
    elements,
):
    with caplog.at_level(DEBUG):
        # calling the start command in dry_run
        assert await start(CommandConfig(dry_run=True)) is not None

        assert "Event to publish found" in caplog.text
        assert (
            "Executing in dry run mode. No event is going to be published."
            in caplog.text
        )
        assert (
            message_collector == []
        )  # the configured publisher shouldn't be called if in dry run mode

        # calling the start command in normal mode
        assert await start(CommandConfig(dry_run=False)) is not None
        assert message_collector == [
            "test event|Some description"
        ]  # the publisher should now have published one message
        all_events = (
            await Event.all()
            .prefetch_related("publications")
            .prefetch_related("publications__publisher")
        )

        # verify that the dry run doesn't mistakenly does double saves
        assert len(all_events) == len(elements), all_events
