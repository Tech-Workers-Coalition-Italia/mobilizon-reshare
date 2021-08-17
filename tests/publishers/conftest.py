from datetime import datetime, timedelta

import pytest

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.abstract import AbstractPublisher
from mobilizon_reshare.publishers.exceptions import PublisherError


@pytest.fixture
def test_event():

    now = datetime.now()
    return MobilizonEvent(
        **{
            "name": "TestName",
            "description": "TestDescr",
            "begin_datetime": now,
            "end_datetime": now + timedelta(hours=1),
            "mobilizon_link": "",
            "mobilizon_id": "",
        }
    )


@pytest.fixture
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


@pytest.fixture
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
