import logging

from fastapi import FastAPI
from tortoise.contrib.pydantic import pydantic_model_creator

from mobilizon_reshare.models.event import Event
from mobilizon_reshare.storage.db import init as init_db, get_db_url

app = FastAPI()
event_pydantic = pydantic_model_creator(Event)


logger = logging.getLogger(__name__)


def check_database():
    url = get_db_url()
    if url.scheme == "sqlite":
        logger.warning(
            "Database is SQLite. This might create issues when running the web application. Please use a "
            "PostgreSQL or MariaDB backend."
        )


def register_endpoints(app):
    @app.get("/events", status_code=200)
    async def get_event():

        return await event_pydantic.from_queryset(Event.all())


@app.on_event("startup")
async def init_app():
    check_database()
    await init_db()
    register_endpoints(app)
    return app
