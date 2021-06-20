from dataclasses import dataclass, asdict
from enum import IntEnum
from typing import Optional

import arrow
import tortoise.timezone
from jinja2 import Template

from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import PublicationStatus


class NotificationStatus(IntEnum):
    WAITING = 1
    FAILED = 2
    PARTIAL = 3
    COMPLETED = 4


@dataclass
class MobilizonEvent:
    """Class representing an event retrieved from Mobilizon."""

    name: str
    description: Optional[str]
    begin_datetime: arrow.Arrow
    end_datetime: arrow.Arrow
    mobilizon_link: str
    mobilizon_id: str
    thumbnail_link: Optional[str] = None
    location: Optional[str] = None
    publication_time: Optional[arrow.Arrow] = None
    publication_status: PublicationStatus = PublicationStatus.WAITING

    def __post_init__(self):
        assert self.begin_datetime.tzinfo == self.end_datetime.tzinfo
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

    def to_model(self) -> Event:
        return Event(
            name=self.name,
            description=self.description,
            mobilizon_id=self.mobilizon_id,
            mobilizon_link=self.mobilizon_link,
            thumbnail_link=self.thumbnail_link,
            location=self.location,
            begin_datetime=self.begin_datetime.astimezone(self.begin_datetime.tzinfo),
            end_datetime=self.end_datetime.astimezone(self.end_datetime.tzinfo),
        )

    @staticmethod
    def from_model(event: Event, tz: str = "UTC"):
        # await Event.filter(id=event.id).values("id", "name", tournament="tournament__name")
        return MobilizonEvent(
            name=event.name,
            description=event.description,
            begin_datetime=arrow.get(
                tortoise.timezone.localtime(value=event.begin_datetime, timezone=tz)
            ),
            end_datetime=arrow.get(
                tortoise.timezone.localtime(value=event.end_datetime, timezone=tz)
            ),
            mobilizon_link=event.mobilizon_link,
            mobilizon_id=event.mobilizon_id,
            thumbnail_link=event.thumbnail_link,
            location=event.location,
            # TODO: Discuss publications
            # publication_time=tortoise.timezone.localtime(value=event.publications, timezone=tz),
            # publication_status=PublicationStatus.WAITING
        )
