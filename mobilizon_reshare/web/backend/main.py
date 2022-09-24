from fastapi import FastAPI
from tortoise.contrib.pydantic import pydantic_model_creator

from mobilizon_reshare.models.event import Event
from mobilizon_reshare.storage.db import init

app = FastAPI()
event_pydantic = pydantic_model_creator(Event)


def register_endpoints(app):
    @app.get("/events", status_code=200)
    async def get_event():

        return await event_pydantic.from_queryset(Event.all())


@app.on_event("startup")
async def init_app():
    await init()
    register_endpoints(app)
    return app
