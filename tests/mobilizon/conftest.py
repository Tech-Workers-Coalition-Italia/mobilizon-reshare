import pytest
import responses

from mobilizon_bots.config.config import settings


@pytest.fixture
def mobilizon_url():
    return settings["source"]["mobilizon"]["url"]


@responses.activate
@pytest.fixture
def mock_mobilizon_success_answer(mobilizon_answer, mobilizon_url):
    with responses.RequestsMock() as rsps:

        rsps.add(
            responses.POST, mobilizon_url, json=mobilizon_answer, status=200,
        )
        yield


@responses.activate
@pytest.fixture
def mock_mobilizon_failure_answer(mobilizon_url):
    with responses.RequestsMock() as rsps:

        rsps.add(
            responses.POST, mobilizon_url, status=500,
        )
        yield
