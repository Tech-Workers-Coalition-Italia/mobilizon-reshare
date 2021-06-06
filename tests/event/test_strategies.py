import arrow
import pytest

from mobilizon_bots.config.config import settings
from mobilizon_bots.event.event_selector import (
    SelectNextEventStrategy,
    select_event_to_publish,
)


@pytest.fixture
def set_break_window_config(desired_break_window_days):
    settings.update(
        {
            "selection.strategy_options.break_between_events_in_minutes": desired_break_window_days
            * 24
            * 60
        }
    )


@pytest.fixture
def set_strategy(strategy_name):
    settings.update({"selection.strategy": strategy_name})


@pytest.mark.parametrize(
    "desired_break_window_days,days_passed_from_publication", [[2, 1], [3, 2]]
)
def test_window_simple_no_event(
    event_generator,
    desired_break_window_days,
    days_passed_from_publication,
    set_break_window_config,
):
    "Testing that the break between events is respected"
    unpublished_events = [
        event_generator(
            published=False,
            begin_date=arrow.Arrow(year=2021, month=1, day=5, hour=11, minute=30),
        )
    ]
    published_events = [
        event_generator(
            published=True,
            publication_time=arrow.now().shift(days=-days_passed_from_publication),
        )
    ]

    selected_event = SelectNextEventStrategy().select(
        published_events, unpublished_events
    )
    assert selected_event is None


@pytest.mark.parametrize(
    "desired_break_window_days,days_passed_from_publication", [[1, 2], [2, 10], [4, 4]]
)
@pytest.mark.parametrize("strategy_name", ["next_event"])
def test_window_simple_event_found(
    event_generator,
    desired_break_window_days,
    days_passed_from_publication,
    set_break_window_config,
    set_strategy,
):
    "Testing that the break between events is respected and an event is found"
    unpublished_events = [
        event_generator(
            published=False,
            begin_date=arrow.Arrow(year=2021, month=1, day=5, hour=11, minute=30),
        )
    ]
    published_events = [
        event_generator(
            published=True,
            publication_time=arrow.now().shift(days=-days_passed_from_publication),
        )
    ]

    selected_event = select_event_to_publish(published_events, unpublished_events)
    assert selected_event is unpublished_events[0]


@pytest.mark.parametrize(
    "desired_break_window_days,days_passed_from_publication", [[1, 2], [2, 10], [4, 4]]
)
@pytest.mark.parametrize("strategy_name", ["next_event"])
def test_window_multi_event_found(
    event_generator,
    desired_break_window_days,
    days_passed_from_publication,
    set_break_window_config,
    set_strategy,
):
    "Testing that the break between events is respected when there are multiple events"
    unpublished_events = [
        event_generator(
            published=False,
            begin_date=arrow.Arrow(year=2022, month=1, day=5, hour=11, minute=30),
        ),
        event_generator(
            published=False,
            begin_date=arrow.Arrow(year=2022, month=3, day=5, hour=11, minute=30),
        ),
        event_generator(
            published=False,
            begin_date=arrow.Arrow(year=2021, month=1, day=5, hour=11, minute=30),
        ),
    ]
    published_events = [
        event_generator(
            published=True,
            publication_time=arrow.now().shift(days=-days_passed_from_publication),
        ),
        event_generator(
            published=True,
            publication_time=arrow.now().shift(days=-days_passed_from_publication - 2),
        ),
        event_generator(
            published=True,
            publication_time=arrow.now().shift(days=-days_passed_from_publication - 4),
        ),
    ]

    selected_event = select_event_to_publish(published_events, unpublished_events)
    assert selected_event is unpublished_events[0]
