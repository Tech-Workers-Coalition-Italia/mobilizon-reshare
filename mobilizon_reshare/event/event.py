from dataclasses import dataclass, asdict
from enum import IntEnum
from typing import Optional, Set
from uuid import UUID

import arrow
import tortoise.timezone
from jinja2 import Template

from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import PublicationStatus, Publication


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
    thumbnail_link: Optional[str] = None
    location: Optional[str] = None
    publication_time: Optional[dict[str, arrow.Arrow]] = None
    status: EventPublicationStatus = EventPublicationStatus.WAITING

    def __post_init__(self):
        assert self.begin_datetime.tzinfo == self.end_datetime.tzinfo
        assert self.begin_datetime < self.end_datetime
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
    def compute_status(publications: list[Publication]) -> EventPublicationStatus:
        unique_statuses: Set[PublicationStatus] = set(
            pub.status for pub in publications
        )

        if PublicationStatus.FAILED in unique_statuses:
            return EventPublicationStatus.FAILED
        elif unique_statuses == {
            PublicationStatus.COMPLETED,
            PublicationStatus.WAITING,
        }:
            return EventPublicationStatus.PARTIAL
        elif len(unique_statuses) == 1:
            return EventPublicationStatus[unique_statuses.pop().name]

        raise ValueError(f"Illegal combination of PublicationStatus: {unique_statuses}")

    @staticmethod
    def from_model(event: Event, tz: str = "UTC"):
        publication_status = MobilizonEvent.compute_status(list(event.publications))
        return MobilizonEvent(
            name=event.name,
            description=event.description,
            begin_datetime=arrow.get(
                tortoise.timezone.localtime(value=event.begin_datetime, timezone=tz)
            ).to("local"),
            end_datetime=arrow.get(
                tortoise.timezone.localtime(value=event.end_datetime, timezone=tz)
            ).to("local"),
            mobilizon_link=event.mobilizon_link,
            mobilizon_id=event.mobilizon_id,
            thumbnail_link=event.thumbnail_link,
            location=event.location,
            publication_time={
                pub.publisher.name: arrow.get(
                    tortoise.timezone.localtime(value=pub.timestamp, timezone=tz)
                ).to("local")
                for pub in event.publications
            }
            if publication_status != PublicationStatus.WAITING
            else None,
            status=publication_status,
        )
