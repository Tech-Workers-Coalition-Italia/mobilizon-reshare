import pytest
from httpx import AsyncClient

from mobilizon_reshare.web.backend.main import app, register_endpoints


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client():
    register_endpoints(app)
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
