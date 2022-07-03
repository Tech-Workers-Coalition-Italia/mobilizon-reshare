from logging import DEBUG, INFO

import pytest

from mobilizon_reshare.storage.query.read import (
    get_all_events,
    events_without_publications,
)
from tests.commands.conftest import (
    second_event_element,
    first_event_element,
)
from mobilizon_reshare.main.pull import pull
from mobilizon_reshare.main.start import start
from tests.conftest import event_0, event_1

empty_specification = {"event": 0, "publications": [], "publisher": []}
one_unpublished_event_specification = {
    "event": 1,
    "publications": [],
    "publisher": ["telegram"],
}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "elements, expected_result", [[[], []]],
)
async def test_pull_no_event(
    generate_models,
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    elements,
    expected_result,
):
    await generate_models(empty_specification)
    with caplog.at_level(DEBUG):
        assert await pull() == []
        assert "Pulled 0 events from Mobilizon." in caplog.text
        assert "There are now 0 unpublished events." in caplog.text

        assert expected_result == await get_all_events()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "elements, specification, expected_result",
    [
        [[second_event_element()], empty_specification, [event_1]],
        [
            [second_event_element()],
            one_unpublished_event_specification,
            [event_0, event_1],
        ],
        [[first_event_element()], one_unpublished_event_specification, [event_0]],
    ],
)
async def test_pull(
    generate_models,
    mock_mobilizon_success_answer,
    mobilizon_answer,
    caplog,
    elements,
    specification,
    expected_result,
):
    await generate_models(specification)
    with caplog.at_level(DEBUG):
        assert await pull() == expected_result
        assert f"Pulled {len(elements)} events from Mobilizon." in caplog.text
        assert expected_result == await get_all_events()

        assert (
            f"There are now {len(expected_result)} unpublished events." in caplog.text
        )
        assert expected_result == await events_without_publications()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.parametrize(
    "elements, specification, expected_pull, expected_publish",
    [
        [
            [second_event_element(), first_event_element()],
            empty_specification,
            [event_0, event_1],
            event_0,
        ],
    ],
)
async def test_pull_start(
    generate_models,
    mock_mobilizon_success_answer,
    mock_publisher_config,
    mobilizon_answer,
    caplog,
    message_collector,
    elements,
    specification,
    expected_pull,
    expected_publish,
    command_config,
):
    await generate_models(specification)

    # I clean the message collector
    message_collector.data = []

    with caplog.at_level(INFO):
        assert await pull() == expected_pull
        assert expected_pull == await get_all_events()
        assert expected_pull == await events_without_publications()

        report = await start(command_config)
        assert report.successful

        assert f"Event to publish found: {expected_publish.name}" in caplog.text

        pull_ids = set(event.mobilizon_id for event in expected_pull)
        publish_ids = {expected_publish.mobilizon_id}

        assert pull_ids == set(event.mobilizon_id for event in await get_all_events())
        assert (pull_ids - publish_ids) == set(
            event.mobilizon_id for event in await events_without_publications()
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.parametrize(
    "elements, specification, expected_result",
    [[[second_event_element()], one_unpublished_event_specification, event_0]],
)
async def test_start_pull(
    generate_models,
    mock_mobilizon_success_answer,
    mock_publisher_config,
    mobilizon_answer,
    caplog,
    message_collector,
    elements,
    specification,
    expected_result,
    command_config,
):
    await generate_models(specification)

    # I clean the message collector
    message_collector.data = []

    with caplog.at_level(DEBUG):
        assert await start(command_config)
        assert f"Event to publish found: {expected_result.name}" in caplog.text
        assert await pull()
        assert "There are now 1 unpublished events."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "multiple_elements, specification, expected_first, expected_last",
    [
        [
            [[second_event_element()], [second_event_element(), first_event_element()]],
            empty_specification,
            [event_1],
            [event_1, event_0],
        ],
    ],
)
async def test_multiple_pull(
    generate_models,
    mock_multiple_success_answer,
    multiple_answers,
    caplog,
    message_collector,
    multiple_elements,
    specification,
    expected_first,
    expected_last,
):
    await generate_models(specification)
    with caplog.at_level(DEBUG):
        assert await pull()
        assert f"There are now {len(expected_first)} unpublished events." in caplog.text
        assert expected_first == await get_all_events()
        assert await events_without_publications() == await get_all_events()

        # I clean the message collector
        message_collector.data = []

        assert await pull()

        assert f"Pulled {len(expected_last)} events from Mobilizon." in caplog.text
        assert f"There are now {len(expected_last)} unpublished events." in caplog.text

        assert set(event.mobilizon_id for event in expected_last) == set(
            event.mobilizon_id for event in await get_all_events()
        )
        assert await events_without_publications() == await get_all_events()
