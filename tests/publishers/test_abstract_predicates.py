import pytest

from datetime import datetime, timedelta

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.publishers.abstract import AbstractPublisher
from mobilizon_bots.publishers.exceptions import PublisherError


@pytest.fixture
def test_event():
    class TestMobilizonEvent(MobilizonEvent):
        pass

    now = datetime.now()
    return TestMobilizonEvent(
        **{
            "name": "TestName",
            "description": "TestDescr",
            "begin_datetime": now,
            "end_datetime": now + timedelta(hours=1),
            "last_accessed": now,
            "mobilizon_link": "",
            "mobilizon_id": "",
        }
    )


def mock_publisher_valid(event):
    class MockPublisher(AbstractPublisher):
        def validate_event(self) -> None:
            pass

        def get_message_from_event(self) -> str:
            return self.event.description

        def validate_credentials(self) -> None:
            pass

        def post(self) -> bool:
            return True

        def validate_message(self) -> None:
            pass

    return MockPublisher(event)


def mock_publisher_invalid(event):
    class MockPublisher(AbstractPublisher):
        def validate_event(self) -> None:
            raise PublisherError("Invalid event")

        def get_message_from_event(self) -> str:
            return ""

        def validate_credentials(self) -> None:
            raise PublisherError("Invalid credentials")

        def post(self) -> bool:
            return False

        def validate_message(self) -> None:
            raise PublisherError("Invalid message")

    return MockPublisher(event)


def test_are_credentials_valid(test_event):
    assert mock_publisher_valid(test_event).are_credentials_valid()


def test_are_credentials_valid_false(test_event):
    assert not mock_publisher_invalid(test_event).are_credentials_valid()


def test_is_event_valid(test_event):
    assert mock_publisher_valid(test_event).is_event_valid()


def test_is_event_valid_false(test_event):
    assert not mock_publisher_invalid(test_event).is_event_valid()


def test_is_message_valid(test_event):
    assert mock_publisher_valid(test_event).is_message_valid()


def test_is_message_valid_false(test_event):
    assert not mock_publisher_invalid(test_event).is_message_valid()
