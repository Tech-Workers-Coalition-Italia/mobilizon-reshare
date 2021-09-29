def test_is_event_valid(mock_formatter_valid, event):
    assert mock_formatter_valid.is_event_valid(event)


def test_is_event_valid_false(mock_formatter_invalid, event):
    assert not mock_formatter_invalid.is_event_valid(event)


def test_is_message_valid(mock_formatter_valid, event):
    assert mock_formatter_valid.is_message_valid(event)


def test_is_message_valid_false(mock_formatter_invalid, event):
    assert not mock_formatter_invalid.is_message_valid(event)
