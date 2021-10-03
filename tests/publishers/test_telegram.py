from mobilizon_reshare.publishers.platforms.telegram import TelegramFormatter


def test_message_length_success(event):
    message = "a" * 500
    event.description = message
    assert TelegramFormatter().is_message_valid(event)


def test_message_length_failure(event):
    message = "a" * 10000
    event.description = message
    assert not TelegramFormatter().is_message_valid(event)
