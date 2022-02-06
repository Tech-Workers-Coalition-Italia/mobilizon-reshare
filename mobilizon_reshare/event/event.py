from dataclasses import dataclass, asdict
from enum import IntEnum
from typing import Optional
from uuid import UUID

import arrow
from jinja2 import Template


class EventPublicationStatus(IntEnum):
    WAITING = 1
    FAILED = 2
    COMPLETED = 3
    PARTIAL = 4


@dataclass
class MobilizonEvent:
    """Class representing an event retrieved from Mobilizon."""

    name: str
    description: Optional[str]
    begin_datetime: arrow.Arrow
    end_datetime: arrow.Arrow
    mobilizon_link: str
    mobilizon_id: UUID
    last_update_time: arrow.Arrow
    thumbnail_link: Optional[str] = None
    location: Optional[str] = None
    publication_time: Optional[dict[str, arrow.Arrow]] = None
    status: EventPublicationStatus = EventPublicationStatus.WAITING

    def __post_init__(self):
        assert self.begin_datetime.tzinfo == self.end_datetime.tzinfo
        assert self.begin_datetime < self.end_datetime
        if self.publication_time is None:
            self.publication_time = {}
        if self.publication_time:
            assert self.status in [
                EventPublicationStatus.COMPLETED,
                EventPublicationStatus.PARTIAL,
                EventPublicationStatus.FAILED,
            ]

    def _fill_template(self, pattern: Template) -> str:
        return pattern.render(**asdict(self))

    def format(self, pattern: Template) -> str:
        return self._fill_template(pattern)
