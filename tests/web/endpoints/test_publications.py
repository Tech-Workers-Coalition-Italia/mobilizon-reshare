import json

import pytest
from httpx import AsyncClient

from mobilizon_reshare.models.publication import Publication


@pytest.mark.asyncio
async def test_publication(client: AsyncClient, failed_publication):

    response = await client.get("/publications")
    assert response.status_code == 200
    expected = await Publication.to_pydantic().from_tortoise_orm(failed_publication)
    assert response.json()["items"][0] == json.loads(expected.json())
