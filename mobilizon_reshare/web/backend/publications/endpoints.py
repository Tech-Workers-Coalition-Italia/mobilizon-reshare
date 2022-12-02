from fastapi_pagination import Page

from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.web import transform_and_paginate


def register_endpoints(app):
    @app.get(
        "/publications", status_code=200, response_model=Page[Publication.to_pydantic()]
    )
    async def get_publications():
        return await transform_and_paginate(Publication, await Publication.all())
