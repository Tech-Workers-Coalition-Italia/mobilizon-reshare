import pytest
import requests

from mobilizon_reshare.publishers.exceptions import InvalidEvent, InvalidResponse
from mobilizon_reshare.publishers.platforms.telegram import (
    TelegramFormatter,
    TelegramPublisher,
)


def test_message_length_success(event):
    message = "a" * 500
    event.description = message
    assert TelegramFormatter().is_message_valid(event)


def test_message_length_failure(event):
    message = "a" * 10000
    event.description = message
    assert not TelegramFormatter().is_message_valid(event)


@pytest.mark.parametrize(
    "message, result",
    [
        ["", ""],
        ["a#b", "ab"],
        ["-", "\\-"],
        ["(", "\\("],
        ["!", "\\!"],
        [")", "\\)"],
        [")!", "\\)\\!"],
    ],
)
def test_escape_message(message, result):
    assert TelegramFormatter().escape_message(message) == result


def test_event_validation(event):
    event.description = None
    with pytest.raises(InvalidEvent):
        TelegramFormatter().validate_event(event)


def test_validate_response():
    response = requests.Response()
    response.status_code = 200
    response._content = b"""{"ok":true}"""
    TelegramPublisher()._validate_response(response)


def test_validate_response_invalid_json():
    response = requests.Response()
    response.status_code = 200
    response._content = b"""{"osxsa"""
    with pytest.raises(InvalidResponse) as e:
        TelegramPublisher()._validate_response(response)

    e.match("json")


def test_validate_response_invalid_request():
    response = requests.Response()
    response.status_code = 400
    response._content = b"""{"error":true}"""
    with pytest.raises(InvalidResponse) as e:

        TelegramPublisher()._validate_response(response)

    e.match("Server returned invalid data")


def test_validate_response_invalid_response():
    response = requests.Response()
    response.status_code = 200
    response._content = b"""{"error":true}"""
    with pytest.raises(InvalidResponse) as e:

        TelegramPublisher()._validate_response(response)

    e.match("Invalid request")
