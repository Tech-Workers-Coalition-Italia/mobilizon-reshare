from logging import DEBUG, INFO

import pytest

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
    "elements",
    [[]],
)
async def test_pull_no_event(
    generate_models, mock_mobilizon_success_answer, mobilizon_answer, caplog, elements
):
    await generate_models(empty_specification)
    with caplog.at_level(DEBUG):
        assert await pull() == []
        assert "Pulled 0 events from Mobilizon." in caplog.text
        assert "There are now 0 unpublished events." in caplog.text


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
        assert (
            f"There are now {len(expected_result)} unpublished events." in caplog.text
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.parametrize(
    "elements, specification, expected_result",
    [
        [[second_event_element()], empty_specification, event_1],
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
    expected_result,
):
    await generate_models(specification)

    # I clean the message collector
    message_collector.data = []

    with caplog.at_level(INFO):
        assert await pull()
        assert await start()
        assert f"Event to publish found: {expected_result.name}" in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.parametrize(
    "elements, specification, expected_result",
    [
        [[second_event_element()], one_unpublished_event_specification, event_0],
    ],
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
):
    await generate_models(specification)

    # I clean the message collector
    message_collector.data = []

    with caplog.at_level(DEBUG):
        assert await start()
        assert f"Event to publish found: {expected_result.name}" in caplog.text
        assert await pull()
        assert "There are now 1 unpublished events."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "multiple_elements, specification",
    [
        [
            [[second_event_element()], [second_event_element(), first_event_element()]],
            empty_specification,
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
):
    await generate_models(specification)
    with caplog.at_level(DEBUG):
        assert await pull()
        assert "There are now 1 unpublished events." in caplog.text

        # I clean the message collector
        message_collector.data = []

        assert await pull()

        assert "Pulled 1 events from Mobilizon." in caplog.text
        assert "There are now 2 unpublished events." in caplog.text
