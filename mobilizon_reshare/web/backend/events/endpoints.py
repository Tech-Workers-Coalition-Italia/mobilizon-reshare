from mobilizon_reshare.models.event import Event
from mobilizon_reshare.storage.query.read import get_all_events


def register_endpoints(app):
    @app.get("/events", status_code=200)
    async def get_events():
        all_events = await get_all_events()
        return [await Event.to_pydantic().from_tortoise_orm(x) for x in all_events]
