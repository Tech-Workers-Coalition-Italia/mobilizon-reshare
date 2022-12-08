from dataclasses import dataclass
from typing import List, Iterator
from uuid import UUID

from tortoise.transactions import atomic

from mobilizon_reshare.dataclasses.event import _MobilizonEvent
from mobilizon_reshare.models.publication import Publication
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
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


@dataclass
class RecapPublication(BasePublication):
    events: List[_MobilizonEvent]


@atomic()
async def build_publications_for_event(
    event: _MobilizonEvent, publishers: Iterator[str]
) -> list[_EventPublication]:
    publication_models = await event.to_model().build_publications(publishers)
    return [_EventPublication.from_orm(m, event) for m in publication_models]
