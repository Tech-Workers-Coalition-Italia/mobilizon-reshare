import pytest
import urllib3
from httpx import AsyncClient

from mobilizon_reshare.storage import db
from mobilizon_reshare.web.backend.main import app, init_endpoints


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client():
    init_endpoints(app)

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def mock_sqlite_db(monkeypatch):
    def get_url():
        return urllib3.util.parse_url("sqlite://memory")

    monkeypatch.setattr(db, "get_db_url", get_url)
