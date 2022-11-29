import json

import pytest
from httpx import AsyncClient

from mobilizon_reshare.models.event import Event


@pytest.mark.anyio
async def test_events(client: AsyncClient, event_model_generator):
    event = event_model_generator()
    await event.save()

    response = await client.get("/events")
    assert response.status_code == 200
    expected = await Event.to_pydantic().from_tortoise_orm(event)
    assert response.json()[0] == json.loads(expected.json())
