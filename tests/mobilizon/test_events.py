import pytest
import arrow

from mobilizon_bots.event.event import PublicationStatus, MobilizonEvent
from mobilizon_bots.mobilizon.events import get_mobilizon_future_events


@pytest.mark.parametrize(
    "mobilizon_answer", [{"data": {"group": {"organizedEvents": {"elements": []}}}}]
)
def test_get_mobilizon_future_events(mock_mobilizon_success_answer):
    """
    Testing a response with no content
    """
    assert get_mobilizon_future_events() == []


@pytest.mark.parametrize(
    "mobilizon_answer",
    [
        {
            "data": {
                "group": {
                    "organizedEvents": {
                        "elements": [
                            {
                                "beginsOn": "2021-05-23T12:15:00Z",
                                "description": None,
                                "endsOn": "2021-05-23T15:15:00Z",
                                "onlineAddress": None,
                                "options": {"showEndTime": True, "showStartTime": True},
                                "physicalAddress": None,
                                "picture": None,
                                "title": "test event",
                                "url": "https://apero.bzh/events/1e2e5943-4a5c-497a-b65d-90457b715d7b",
                                "uuid": "1e2e5943-4a5c-497a-b65d-90457b715d7b",
                            }
                        ]
                    }
                }
            }
        }
    ],
)
def test_simple_event(mock_mobilizon_success_answer):
    """
    Testing a minimal event that is valid in Mobilizon
    """
    assert get_mobilizon_future_events() == [
        MobilizonEvent(
            name="test event",
            description=None,
            begin_datetime=arrow.get("2021-05-23T12:15:00Z"),
            end_datetime=arrow.get("2021-05-23T15:15:00Z"),
            mobilizon_link="https://apero.bzh/events/1e2e5943-4a5c-497a-b65d-90457b715d7b",
            mobilizon_id="1e2e5943-4a5c-497a-b65d-90457b715d7b",
            thumbnail_link=None,
            location=None,
            publication_time=None,
            publication_status=PublicationStatus.WAITING,
        )
    ]
