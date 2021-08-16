from datetime import datetime, timedelta

import pytest

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.abstract import AbstractPublisher
from mobilizon_reshare.publishers.exceptions import PublisherError


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

        def publish(self) -> bool:
            return True

        def validate_message(self) -> None:
            pass

        def _send(self, message):
            pass

        def _validate_response(self, response) -> None:
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

        def publish(self) -> bool:
            return False

        def validate_message(self) -> None:
            raise PublisherError("Invalid message")

        def _send(self, message):
            pass

        def _validate_response(self, response) -> None:
            pass

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
