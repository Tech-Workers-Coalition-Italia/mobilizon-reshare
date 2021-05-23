from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Optional

import arrow
from jinja2 import Template


class PublicationStatus(Enum):
    WAITING = 1
    FAILED = 2
    PARTIAL = 3
    COMPLETED = 4


@dataclass
class MobilizonEvent:
    """Class representing an event retrieved from Mobilizon."""

    name: str
    description: Optional[str]
    begin_datetime: Optional[arrow.Arrow]
    end_datetime: Optional[arrow.Arrow]
    mobilizon_link: Optional[str]
    mobilizon_id: str
    thumbnail_link: Optional[str] = None
    location: Optional[str] = None
    publication_time: Optional[arrow.Arrow] = None
    publication_status: PublicationStatus = PublicationStatus.WAITING
    last_accessed: arrow.Arrow = field(compare=False, default=None)

    def __post_init__(self):
        if self.begin_datetime and self.end_datetime:
            assert self.begin_datetime < self.end_datetime
        if self.publication_time:
            assert self.publication_status in [
                PublicationStatus.COMPLETED,
                PublicationStatus.PARTIAL,
            ]

    def _fill_template(self, pattern: Template) -> str:
        return pattern.render(**asdict(self))

    def format(self, pattern: Template) -> str:
        return self._fill_template(pattern)
