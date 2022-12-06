from dataclasses import dataclass
from typing import List
from uuid import UUID

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
