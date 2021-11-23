import pytest

import mobilizon_reshare.storage.query.read
from mobilizon_reshare.models.publisher import Publisher


@pytest.fixture(scope="function")
async def mock_active_publishers(request, monkeypatch):
    for name in request.param:
        await Publisher.create(name=name)

    def _mock_active_pub():
        return request.param

    monkeypatch.setattr(
        mobilizon_reshare.storage.query.read, "get_active_publishers", _mock_active_pub
    )

    return request.param
