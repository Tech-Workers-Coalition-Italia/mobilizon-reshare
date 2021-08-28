import pytest
import responses

from mobilizon_reshare.config.config import get_settings


@pytest.fixture
def mobilizon_url():
    return get_settings()["source"]["mobilizon"]["url"]


@responses.activate
@pytest.fixture
def mock_mobilizon_success_answer(mobilizon_answer, mobilizon_url):
    with responses.RequestsMock() as rsps:

        rsps.add(
            responses.POST,
            mobilizon_url,
            json=mobilizon_answer,
            status=200,
        )
        yield


@responses.activate
@pytest.fixture
def mock_mobilizon_failure_answer(mobilizon_url):
    with responses.RequestsMock() as rsps:

        rsps.add(
            responses.POST,
            mobilizon_url,
            status=500,
        )
        yield
