import pytest
import responses

from mobilizon_bots.config.config import settings


@responses.activate
@pytest.fixture
def mock_mobilizon_success_answer(mobilizon_answer):
    with responses.RequestsMock() as rsps:

        rsps.add(
            responses.POST,
            settings["source"]["mobilizon"]["url"],
            json=mobilizon_answer,
            status=200,
        )
        yield
