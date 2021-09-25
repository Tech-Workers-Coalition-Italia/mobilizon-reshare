from datetime import datetime, timedelta
from uuid import UUID

import pytest
import responses

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.abstract import AbstractPublisher
from mobilizon_reshare.publishers.exceptions import PublisherError, InvalidResponse

api_uri = "https://zulip.twc-italia.org/api/v1/"
users_me = {
    "result": "success",
    "msg": "",
    "email": "giacomotest2-bot@zulip.twc-italia.org",
    "user_id": 217,
    "avatar_version": 1,
    "is_admin": False,
    "is_owner": False,
    "is_guest": False,
    "is_bot": True,
    "full_name": "Bot test Giacomo2",
    "timezone": "",
    "is_active": True,
    "date_joined": "2021-09-13T19:36:45.857782+00:00",
    "avatar_url": "https://secure.gravatar.com/avatar/d2d9a932bf9ff69d4e3cdf2203271500",
    "bot_type": 1,
    "bot_owner_id": 14,
    "max_message_id": 8048,
}


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
            "mobilizon_id": UUID(int=0),
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

        def validate_message(self) -> None:
            raise PublisherError("Invalid message")

        def _send(self, message):
            pass

        def _validate_response(self, response) -> None:
            pass

    return MockPublisher(event)


@pytest.fixture
def mock_publisher_invalid_response(mock_publisher_invalid, event):
    class MockPublisher(type(mock_publisher_invalid)):
        def validate_event(self) -> None:
            pass

        def validate_credentials(self) -> None:
            pass

        def validate_message(self) -> None:
            pass

        def _validate_response(self, response) -> None:
            raise InvalidResponse("Invalid response")

    return MockPublisher(event)


@pytest.fixture
def mocked_valid_response():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            api_uri + "users/me",
            json=users_me,
            status=200,
        )
        rsps.add(
            responses.POST,
            api_uri + "messages",
            json={"result": "success", "msg": "", "id": 8049},
            status=200,
        )
        yield


@pytest.fixture
def mocked_credential_error_response():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            api_uri + "users/me",
            json={"result": "error", "msg": "Your credentials are not valid!"},
            status=403,
        )
        yield


@pytest.fixture
def mocked_client_error_response():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            api_uri + "users/me",
            json=users_me,
            status=200,
        )
        rsps.add(
            responses.POST,
            api_uri + "messages",
            json={"result": "error", "msg": "Invalid request"},
            status=400,
        )
        yield
