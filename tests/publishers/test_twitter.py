from unittest.mock import patch

import pytest
from tweepy import API, TweepyException

from mobilizon_reshare.publishers.exceptions import (
    InvalidMessage,
    InvalidCredentials,
    PublisherError,
)
from mobilizon_reshare.publishers.platforms.twitter import (
    TwitterFormatter,
    TwitterPublisher,
)


def test_message_length_success(event):
    message = "a" * 300
    event.description = message
    assert TwitterFormatter().validate_event(event) is None


def test_message_length_failure(event):
    message = "a" * 10000
    event.name = message

    with pytest.raises(InvalidMessage):
        TwitterFormatter().validate_event(event)


def test_validate_credentials_error():
    with patch.object(API, "verify_credentials", return_value=False) as mock:
        with pytest.raises(InvalidCredentials):
            TwitterPublisher().validate_credentials()
        mock.assert_called()


def test_send_error(event):
    with patch.object(
        API, "update_status", side_effect=TweepyException("some error")
    ) as mock:
        with pytest.raises(PublisherError):
            TwitterPublisher().send("abc", event)
        mock.assert_called()
