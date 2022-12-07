from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate

from mobilizon_reshare.models.publication import Publication


def register_endpoints(app):
    @app.get(
        "/publications", status_code=200, response_model=Page[Publication.to_pydantic()]
    )
    async def get_publications():
        return await paginate(Publication, prefetch_related=True)
