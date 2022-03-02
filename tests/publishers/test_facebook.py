from logging import DEBUG
from unittest.mock import patch

import pytest
from facebook import GraphAPI, GraphAPIError

from mobilizon_reshare.publishers.exceptions import (
    InvalidEvent,
    InvalidMessage,
    PublisherError,
)
from mobilizon_reshare.publishers.platforms.facebook import (
    FacebookFormatter,
    FacebookPublisher,
)


def test_message_length_success(event):
    message = "a" * 500
    event.description = message
    assert FacebookFormatter().validate_event(event) is None


def test_message_length_failure(event):
    message = "a" * 80000
    event.description = message

    with pytest.raises(InvalidMessage):
        FacebookFormatter().validate_event(event)


def test_event_validation(event):
    event.description = None
    with pytest.raises(InvalidEvent):
        FacebookFormatter().validate_event(event)


def test_send_error(event):

    with patch.object(
        GraphAPI, "put_object", side_effect=GraphAPIError("some error")
    ) as mock:
        with pytest.raises(PublisherError):
            FacebookPublisher().send("abc", event)
        mock.assert_called()


def test_validate_credentials_error(event):

    with patch.object(
        GraphAPI, "get_object", side_effect=GraphAPIError("some error")
    ) as mock:
        with pytest.raises(PublisherError):
            FacebookPublisher().validate_credentials()
        mock.assert_called()


def test_validate_credentials(event, caplog):

    with patch.object(GraphAPI, "get_object", return_value=None) as mock:
        with caplog.at_level(DEBUG):
            FacebookPublisher().validate_credentials()
            mock.assert_called()
            assert "Facebook credentials are valid" in caplog.text
