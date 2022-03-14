from logging import DEBUG

import pytest

from tests.commands.conftest import (
    second_event_element,
    first_event_element,
)
from mobilizon_reshare.main.pull import pull
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
