from mobilizon_reshare.models.publication import Publication


def register_endpoints(app):
    @app.get("/publications", status_code=200)
    async def get_publications():
        return await Publication.to_pydantic().from_queryset(Publication.all())
