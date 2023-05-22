from dataclasses import dataclass
from functools import partial
from typing import List, Iterator
from uuid import UUID

from tortoise.transactions import atomic

from mobilizon_reshare.dataclasses.event import _MobilizonEvent
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.storage.query.read import (
    get_event,
    prefetch_publication_relations,
)


@dataclass
class BasePublication:
    publisher: AbstractPlatform
    formatter: AbstractEventFormatter


@dataclass
class _EventPublication(BasePublication):
    event: _MobilizonEvent
    id: UUID

    @classmethod
    def from_orm(cls, model: Publication, event: _MobilizonEvent):
        # imported here to avoid circular dependencies
        from mobilizon_reshare.publishers.platforms.platform_mapping import (
            get_publisher_class,
            get_formatter_class,
        )

        publisher = get_publisher_class(model.publisher.name)()
        formatter = get_formatter_class(model.publisher.name)()
        return cls(publisher, formatter, event, model.id,)

    @classmethod
    async def retrieve(cls, publication_id):
        publication = await prefetch_publication_relations(
            Publication.get(id=publication_id)
        )
        event = _MobilizonEvent.from_model(publication.event)
        return cls.from_orm(publication, event)


@dataclass
class RecapPublication(BasePublication):
    events: List[_MobilizonEvent]


@dataclass
class _PublicationNotification(BasePublication):
    publication: _EventPublication


@atomic()
async def build_publications_for_event(
    event: _MobilizonEvent, publishers: Iterator[str]
) -> list[_EventPublication]:
    publication_models = await event.to_model().build_publications(publishers)
    return [_EventPublication.from_orm(m, event) for m in publication_models]


async def get_failed_publications_for_event(
    event: _MobilizonEvent,
) -> List[_EventPublication]:
    event_model = await get_event(event.mobilizon_id)
    failed_publications = await event_model.get_failed_publications()
    return list(
        map(partial(_EventPublication.from_orm, event=event), failed_publications)
    )
