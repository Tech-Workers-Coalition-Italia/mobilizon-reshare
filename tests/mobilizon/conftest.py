import pytest
import responses


@responses.activate
@pytest.fixture
def mock_mobilizon_failure_answer(mobilizon_url):
    with responses.RequestsMock() as rsps:

        rsps.add(
            responses.POST, mobilizon_url, status=500,
        )
        yield
