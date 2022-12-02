from fastapi_pagination import Page

from mobilizon_reshare.models.event import Event
from mobilizon_reshare.storage.query.read import get_all_events
from mobilizon_reshare.web import transform_and_paginate


def register_endpoints(app):
    @app.get("/events", status_code=200, response_model=Page[Event.to_pydantic()])
    async def get_events():
        all_events = await get_all_events()
        return await transform_and_paginate(Event, all_events)
