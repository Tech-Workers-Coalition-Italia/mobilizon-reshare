from dataclasses import dataclass, asdict
from typing import Optional

import arrow
import tortoise.timezone
from jinja2 import Template

from mobilizon_bots.models.event import Event
from mobilizon_bots.models.publication import PublicationStatus


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
    publication_time: Optional[dict[str, arrow.Arrow]] = None
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
        unique_statuses = set(pub.status for pub in event.publications)
        publication_status = (
            unique_statuses.pop()
            if len(unique_statuses) == 1
            else PublicationStatus.PARTIAL
        )
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
            # TODO: Discuss publications (both time and status)
            publication_time={
                pub.publisher.name: arrow.get(
                    tortoise.timezone.localtime(value=pub.timestamp, timezone=tz)
                )
                for pub in event.publications
            }
            if publication_status != PublicationStatus.WAITING
            else None,
            publication_status=publication_status,
        )
