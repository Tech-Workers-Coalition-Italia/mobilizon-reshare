from datetime import timedelta
from uuid import UUID

import arrow
import pytest

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.publishers.exceptions import PublisherError, InvalidResponse


@pytest.fixture
def test_event():
    now = arrow.now()
    return MobilizonEvent(
        **{
            "name": "TestName",
            "description": "TestDescr",
            "begin_datetime": now,
            "end_datetime": now + timedelta(hours=1),
            "mobilizon_link": "",
            "mobilizon_id": UUID(int=0),
        }
    )


@pytest.fixture
def mock_formatter_valid():
    class MockFormatter(AbstractEventFormatter):
        def validate_event(self, event) -> None:
            pass

        def get_message_from_event(self, event) -> str:
            return event.description

        def validate_message(self, event) -> None:
            pass

        def _send(self, message):
            pass

        def get_recap_fragment(self, event):
            return event.name

    return MockFormatter()


@pytest.fixture
def mock_formatter_invalid():
    class MockFormatter(AbstractEventFormatter):
        def validate_event(self, event) -> None:
            raise PublisherError("Invalid event")

        def get_message_from_event(self, event) -> str:
            return ""

        def validate_message(self, event) -> None:
            raise PublisherError("Invalid message")

    return MockFormatter()


@pytest.fixture
def mock_publisher_valid():
    class MockPublisher(AbstractPlatform):
        def _send(self, message):
            pass

        def _validate_response(self, response):
            pass

        def validate_credentials(self) -> None:
            pass

    return MockPublisher()


@pytest.fixture
def mock_publisher_invalid():
    class MockPublisher(AbstractPlatform):
        def _send(self, message):
            pass

        def _validate_response(self, response):
            return InvalidResponse("error")

        def validate_credentials(self) -> None:
            raise PublisherError("error")

    return MockPublisher()


@pytest.fixture
def mock_publisher_invalid_response():
    class MockPublisher(AbstractPlatform):
        def _send(self, message):
            pass

        def _validate_response(self, response):
            raise InvalidResponse("Invalid response")

        def validate_credentials(self) -> None:
            pass

    return MockPublisher()
