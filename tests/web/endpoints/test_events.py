import json

import pytest
from httpx import AsyncClient

from mobilizon_reshare.web.backend.main import event_pydantic


@pytest.mark.anyio
async def test_events(client: AsyncClient, event_model_generator):
    event = event_model_generator()
    await event.save()

    response = await client.get("/events")
    assert response.status_code == 200
    assert response.json()[0] == [json.loads(event_pydantic.from_orm(event).json())][0]
