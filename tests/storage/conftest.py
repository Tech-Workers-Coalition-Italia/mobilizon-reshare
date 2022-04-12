import pytest

from mobilizon_reshare.models.publisher import Publisher


@pytest.fixture(scope="function")
async def mock_active_publishers(request, monkeypatch):
    for name in request.param:
        await Publisher.create(name=name)

    return request.param
