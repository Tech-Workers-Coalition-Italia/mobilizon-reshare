from collections import UserList
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

        def get_recap_header(self):
            return "Upcoming"

    return MockFormatter()


@pytest.fixture()
def message_collector():
    class MessageCollector(UserList):
        def collect_message(self, message):
            self.append(message)

    return MessageCollector()


@pytest.fixture
def mock_formatter_invalid():
    class MockFormatter(AbstractEventFormatter):
        def validate_event(self, event) -> None:
            raise PublisherError("Invalid event error")

        def get_message_from_event(self, event) -> str:
            return ""

        def validate_message(self, event) -> None:
            raise PublisherError("Invalid message error")

    return MockFormatter()


@pytest.fixture
def mock_publisher_valid(message_collector):
    class MockPublisher(AbstractPlatform):
        name = "mock"

        def _send(self, message):
            message_collector.append(message)

        def _validate_response(self, response):
            pass

        def validate_credentials(self) -> None:
            pass

    return MockPublisher()


@pytest.fixture
def mock_publisher_invalid(message_collector):
    class MockPublisher(AbstractPlatform):

        name = "mock"

        def _send(self, message):
            message_collector.append(message)

        def _validate_response(self, response):
            return InvalidResponse("response error")

        def validate_credentials(self) -> None:
            raise PublisherError("credentials error")

    return MockPublisher()


@pytest.fixture
def mock_publisher_invalid_response(message_collector):
    class MockPublisher(AbstractPlatform):

        name = "mock"

        def _send(self, message):
            message_collector.append(message)

        def _validate_response(self, response):
            raise InvalidResponse("Invalid response")

        def validate_credentials(self) -> None:
            pass

    return MockPublisher()
