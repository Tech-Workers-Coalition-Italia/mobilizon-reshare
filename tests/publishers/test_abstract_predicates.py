def test_are_credentials_valid(test_event, mock_publisher_valid):
    assert mock_publisher_valid.are_credentials_valid()


def test_are_credentials_valid_false(mock_publisher_invalid):
    assert not mock_publisher_invalid.are_credentials_valid()


def test_is_event_valid(mock_publisher_valid):
    assert mock_publisher_valid.is_event_valid()


def test_is_event_valid_false(mock_publisher_invalid):
    assert not mock_publisher_invalid.is_event_valid()


def test_is_message_valid(mock_publisher_valid):
    assert mock_publisher_valid.is_message_valid()


def test_is_message_valid_false(mock_publisher_invalid):
    assert not mock_publisher_invalid.is_message_valid()
