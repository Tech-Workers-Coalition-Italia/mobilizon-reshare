import pytest
import arrow

from mobilizon_bots.event.event import PublicationStatus, MobilizonEvent
from mobilizon_bots.mobilizon.events import (
    get_mobilizon_future_events,
    MobilizonRequestFailed,
    get_unpublished_events,
)

simple_event_element = {
    "beginsOn": "2021-05-23T12:15:00Z",
    "description": None,
    "endsOn": "2021-05-23T15:15:00Z",
    "onlineAddress": None,
    "options": {"showEndTime": True, "showStartTime": True},
    "physicalAddress": None,
    "picture": None,
    "title": "test event",
    "url": "https://some_mobilizon/events/1e2e5943-4a5c-497a-b65d-90457b715d7b",
    "uuid": "1e2e5943-4a5c-497a-b65d-90457b715d7b",
}
simple_event_response = {
    "data": {"group": {"organizedEvents": {"elements": [simple_event_element]}}}
}

full_event_element = {
    "beginsOn": "2021-05-25T15:15:00Z",
    "description": "<p>a description</p>",
    "endsOn": "2021-05-25T16:15:00Z",
    "onlineAddress": "http://some_location",
    "options": {"showEndTime": True, "showStartTime": True},
    "physicalAddress": None,
    "picture": None,
    "title": "full event",
    "url": "https://some_mobilizon/events/56e7ca43-1b6b-4c50-8362-0439393197e6",
    "uuid": "56e7ca43-1b6b-4c50-8362-0439393197e6",
}
full_event_response = {
    "data": {"group": {"organizedEvents": {"elements": [full_event_element]}}}
}

two_events_response = {
    "data": {
        "group": {
            "organizedEvents": {"elements": [simple_event_element, full_event_element]}
        }
    }
}

simple_event = MobilizonEvent(
    name="test event",
    description=None,
    begin_datetime=arrow.get("2021-05-23T12:15:00Z"),
    end_datetime=arrow.get("2021-05-23T15:15:00Z"),
    mobilizon_link="https://some_mobilizon/events/1e2e5943-4a5c-497a-b65d-90457b715d7b",
    mobilizon_id="1e2e5943-4a5c-497a-b65d-90457b715d7b",
    thumbnail_link=None,
    location=None,
)

full_event = MobilizonEvent(
    name="full event",
    description="<p>a description</p>",
    begin_datetime=arrow.get("2021-05-25T15:15:00+00:00]"),
    end_datetime=arrow.get("2021-05-25T16:15:00+00:00"),
    mobilizon_link="https://some_mobilizon/events/56e7ca43-1b6b-4c50-8362-0439393197e6",
    mobilizon_id="56e7ca43-1b6b-4c50-8362-0439393197e6",
    thumbnail_link=None,
    location="http://some_location",
)


@pytest.mark.parametrize(
    "mobilizon_answer, expected_result",
    [
        [{"data": {"group": {"organizedEvents": {"elements": []}}}}, []],
        [simple_event_response, [simple_event]],
        [full_event_response, [full_event]],
        [two_events_response, [simple_event, full_event]],
    ],
)
def test_event_response(mock_mobilizon_success_answer, expected_result):
    """
    Testing the request and parsing logic
    """
    assert get_mobilizon_future_events() == expected_result


def test_failure(mock_mobilizon_failure_answer):
    with pytest.raises(MobilizonRequestFailed):
        get_mobilizon_future_events()


@pytest.mark.parametrize(
    "mobilizon_answer, published_events,expected_result",
    [
        [{"data": {"group": {"organizedEvents": {"elements": []}}}}, [], []],
        [simple_event_response, [], [simple_event]],
        [two_events_response, [], [simple_event, full_event]],
        [two_events_response, [simple_event], [full_event]],
    ],
)
def test_get_unpublished_events(
    mock_mobilizon_success_answer, published_events, expected_result
):
    assert get_unpublished_events(published_events) == expected_result
