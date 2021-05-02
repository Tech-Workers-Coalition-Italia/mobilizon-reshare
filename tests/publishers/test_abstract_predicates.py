import pytest

from mobilizon_bots.publishers.abstract import AbstractPublisher


@pytest.fixture
def mock_publisher_valid():
    class MockPublisher(AbstractPublisher):
        def validate_credentials(self) -> dict:
            return {}

        def validate_event(self) -> dict:
            return {}

        def post(self) -> dict:
            pass

    return MockPublisher({}, {})


@pytest.fixture
def mock_publisher_invalid():
    class MockPublisher(AbstractPublisher):
        def validate_credentials(self) -> dict:
            raise ValueError("Error")

        def validate_event(self) -> dict:
            raise ValueError("Error")

        def post(self) -> dict:
            raise ValueError()

    return MockPublisher({}, {})


def test_are_credentials_valid(mock_publisher_valid):
    assert mock_publisher_valid.are_credentials_valid()


def test_are_credentials_valid_false(mock_publisher_invalid):
    assert not mock_publisher_invalid.are_credentials_valid()


def test_is_event_valid(mock_publisher_valid):
    assert mock_publisher_valid.is_event_valid()


def test_is_event_valid_false(mock_publisher_invalid):
    assert not mock_publisher_invalid.is_event_valid()
