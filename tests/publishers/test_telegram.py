import pytest

from mobilizon_reshare.publishers.exceptions import InvalidEvent
from mobilizon_reshare.publishers.platforms.telegram import TelegramFormatter


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
