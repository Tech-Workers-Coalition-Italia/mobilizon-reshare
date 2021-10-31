from tortoise.transactions import atomic

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.storage.query import CONNECTION_NAME
from mobilizon_reshare.storage.query.read_query import prefetch_event_relations


@atomic(CONNECTION_NAME)
async def create_event_publication_models(event: MobilizonEvent) -> list[Publication]:
    return await (
        await prefetch_event_relations(Event.filter(mobilizon_id=event.mobilizon_id))
    )[0].build_unsaved_publication_models()
