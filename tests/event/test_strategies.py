import arrow
import pytest
from unittest.mock import patch


from more.config.config import get_settings
from more.event.event_selection_strategies import (
    SelectNextEventStrategy,
    select_event_to_publish,
)


@pytest.fixture
def set_break_window_config(desired_break_window_days):
    get_settings().update(
        {
            "selection.strategy_options.break_between_events_in_minutes": desired_break_window_days
            * 24
            * 60
        }
    )


@pytest.fixture
def set_strategy(strategy_name):
    get_settings().update({"selection.strategy": strategy_name})


@pytest.fixture
def mock_publication_window(publication_window):
    begin, end = publication_window
    get_settings().update(
        {"publishing.window.begin": begin, "publishing.window.end": end}
    )


def test_window_no_event():
    selected_event = SelectNextEventStrategy().select([], [])
    assert selected_event is None


@pytest.mark.parametrize("current_hour", [10])
@pytest.mark.parametrize(
    "desired_break_window_days,days_passed_from_publication", [[2, 1], [3, 2]]
)
def test_window_simple_no_event_in_window(
    event_generator,
    desired_break_window_days,
    days_passed_from_publication,
    set_break_window_config,
    mock_arrow_now,
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
            publication_time={
                "telegram": arrow.now().shift(days=-days_passed_from_publication)
            },
        )
    ]

    selected_event = SelectNextEventStrategy().select(
        published_events, unpublished_events
    )
    assert selected_event is None


@pytest.mark.parametrize("current_hour", [15])
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
    mock_arrow_now,
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
            publication_time={
                "telegram": arrow.now().shift(days=-days_passed_from_publication)
            },
        )
    ]

    selected_event = select_event_to_publish(published_events, unpublished_events)
    assert selected_event is unpublished_events[0]


@pytest.mark.parametrize("current_hour", [15])
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
    mock_arrow_now,
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
            publication_time={
                "telegram": arrow.now().shift(days=-days_passed_from_publication)
            },
        ),
        event_generator(
            published=True,
            publication_time={
                "telegram": arrow.now().shift(days=-days_passed_from_publication - 2)
            },
        ),
        event_generator(
            published=True,
            publication_time={
                "telegram": arrow.now().shift(days=-days_passed_from_publication - 4)
            },
        ),
    ]

    selected_event = select_event_to_publish(published_events, unpublished_events)
    assert selected_event is unpublished_events[0]


@pytest.fixture
def mock_arrow_now(current_hour):
    def mock_now():
        return arrow.Arrow(year=2021, month=1, day=1, hour=current_hour)

    with patch("arrow.now", mock_now):
        yield


@pytest.mark.parametrize("current_hour", [14, 15, 16, 18])
@pytest.mark.parametrize("publication_window", [(14, 19)])
def test_publishing_inner_window_true(mock_arrow_now, mock_publication_window):
    """
    Testing that the window check correctly returns True when in an inner publishing window.
    """
    assert SelectNextEventStrategy().is_in_publishing_window()


@pytest.mark.parametrize("current_hour", [2, 10, 11, 19])
@pytest.mark.parametrize("publication_window", [(14, 19)])
def test_publishing_inner_window_false(mock_arrow_now, mock_publication_window):
    """
    Testing that the window check correctly returns False when not in an inner publishing window.
    """
    assert not SelectNextEventStrategy().is_in_publishing_window()


@pytest.mark.parametrize("current_hour", [2, 10, 11, 19])
@pytest.mark.parametrize("publication_window", [(19, 14)])
def test_publishing_outer_window_true(mock_arrow_now, mock_publication_window):
    """
    Testing that the window check correctly returns True when in an outer publishing window.
    """
    assert SelectNextEventStrategy().is_in_publishing_window()


@pytest.mark.parametrize("current_hour", [14, 15, 16, 18])
@pytest.mark.parametrize("publication_window", [(19, 14)])
def test_publishing_outer_window_false(mock_arrow_now, mock_publication_window):
    """
    Testing that the window check correctly returns False when not in an outer publishing window.
    """
    assert not SelectNextEventStrategy().is_in_publishing_window()
