from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate

from mobilizon_reshare.models.event import Event


def register_endpoints(app):
    @app.get("/events", status_code=200, response_model=Page[Event.to_pydantic()])
    async def get_events():
        return await paginate(Event, prefetch_related=True)
