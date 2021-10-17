import pytest
import requests

from mobilizon_reshare.publishers.exceptions import (
    InvalidEvent,
    InvalidResponse,
    ServerError,
    ClientError,
)
from mobilizon_reshare.publishers.platforms.mastodon import (
    MastodonFormatter,
    MastodonPublisher,
)


def test_message_length_success(event):
    message = "a" * 200
    event.name = message
    assert MastodonFormatter().is_message_valid(event)


def test_message_length_failure(event):
    message = "a" * 500
    event.name = message
    assert not MastodonFormatter().is_message_valid(event)


def test_event_validation(event):
    event.description = None
    with pytest.raises(InvalidEvent):
        MastodonFormatter().validate_event(event)


def test_validate_response():
    response = requests.Response()
    response.status_code = 200
    response._content = b"""{"ok":true}"""
    MastodonPublisher()._validate_response(response)


def test_validate_response_invalid_json():
    response = requests.Response()
    response.status_code = 200
    response._content = b"""{"osxsa"""
    with pytest.raises(InvalidResponse) as e:
        MastodonPublisher()._validate_response(response)

    e.match("json")


def test_validate_response_client_error():
    response = requests.Response()
    response.status_code = 403
    response._content = b"""{"error":true}"""
    with pytest.raises(ClientError) as e:
        MastodonPublisher()._validate_response(response)

    e.match("403 ERROR")


def test_validate_response_server_error():
    response = requests.Response()
    response.status_code = 500
    response._content = b"""{"error":true}"""
    with pytest.raises(ServerError) as e:
        MastodonPublisher()._validate_response(response)

    e.match("500 ERROR")
