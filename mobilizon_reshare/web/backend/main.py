import logging

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from mobilizon_reshare.storage.db import init as init_db, get_db_url
from mobilizon_reshare.web.backend.events.endpoints import (
    register_endpoints as register_event_endpoints,
)
from mobilizon_reshare.web.backend.publications.endpoints import (
    register_endpoints as register_publication_endpoints,
)

app = FastAPI()
logger = logging.getLogger(__name__)


def check_database():
    url = get_db_url()
    if url.scheme == "sqlite":
        logger.warning(
            "Database is SQLite. This might create issues when running the web application. Please use a "
            "PostgreSQL or MariaDB backend."
        )


def register_endpoints(app):

    register_event_endpoints(app)
    register_publication_endpoints(app)


def init_endpoints(app):

    register_endpoints(app)
    add_pagination(app)


@app.on_event("startup")
async def init_app(init_logging=True):
    check_database()
    await init_db(init_logging=init_logging)
    init_endpoints(app)
    return app
