from dataclasses import dataclass, asdict
from typing import Optional, Iterable
from uuid import UUID

import arrow
from arrow import Arrow
from jinja2 import Template

from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.dataclasses.event_publication_status import (
    _EventPublicationStatus,
    _compute_event_status,
)
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.storage.query.read import (
    get_all_events,
    get_event,
    get_events_without_publications,
)


@dataclass
class _MobilizonEvent:
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
    status: _EventPublicationStatus = _EventPublicationStatus.WAITING

    def __post_init__(self):
        assert self.begin_datetime.tzinfo == self.end_datetime.tzinfo
        assert self.begin_datetime < self.end_datetime
        if self.publication_time is None:
            self.publication_time = {}
        if self.publication_time:
            assert self.status in [
                _EventPublicationStatus.COMPLETED,
                _EventPublicationStatus.PARTIAL,
                _EventPublicationStatus.FAILED,
            ]

    def _fill_template(self, pattern: Template) -> str:
        config = get_settings()
        return pattern.render(locale=config["locale"], **asdict(self))

    def format(self, pattern: Template) -> str:
        return self._fill_template(pattern)

    @classmethod
    def from_model(cls, event: Event):
        publication_status = _compute_event_status(list(event.publications))
        publication_time = {}

        for pub in event.publications:
            if publication_status != _EventPublicationStatus.WAITING:
                assert pub.timestamp is not None
                publication_time[pub.publisher.name] = arrow.get(pub.timestamp).to(
                    "local"
                )
        return cls(
            name=event.name,
            description=event.description,
            begin_datetime=arrow.get(event.begin_datetime).to("local"),
            end_datetime=arrow.get(event.end_datetime).to("local"),
            mobilizon_link=event.mobilizon_link,
            mobilizon_id=event.mobilizon_id,
            thumbnail_link=event.thumbnail_link,
            location=event.location,
            publication_time=publication_time,
            status=publication_status,
            last_update_time=arrow.get(event.last_update_time).to("local"),
        )

    def to_model(self, db_id: Optional[UUID] = None) -> Event:

        kwargs = {
            "name": self.name,
            "description": self.description,
            "mobilizon_id": self.mobilizon_id,
            "mobilizon_link": self.mobilizon_link,
            "thumbnail_link": self.thumbnail_link,
            "location": self.location,
            "begin_datetime": self.begin_datetime.astimezone(
                self.begin_datetime.tzinfo
            ),
            "end_datetime": self.end_datetime.astimezone(self.end_datetime.tzinfo),
            "last_update_time": self.last_update_time.astimezone(
                self.last_update_time.tzinfo
            ),
        }
        if db_id is not None:
            kwargs.update({"id": db_id})
        return Event(**kwargs)

    @classmethod
    async def retrieve(cls, mobilizon_id):
        return cls.from_model(await get_event(mobilizon_id))


async def get_all_mobilizon_events(
    from_date: Optional[Arrow] = None, to_date: Optional[Arrow] = None,
) -> list[_MobilizonEvent]:
    return [_MobilizonEvent.from_model(event) for event in await get_all_events()]


async def get_published_events(
    from_date: Optional[Arrow] = None, to_date: Optional[Arrow] = None
) -> Iterable[_MobilizonEvent]:
    """
    Retrieves events that are not waiting. Function could be renamed to something more fitting
    :return:
    """
    return await get_mobilizon_events_with_status(
        [
            _EventPublicationStatus.COMPLETED,
            _EventPublicationStatus.PARTIAL,
            _EventPublicationStatus.FAILED,
        ],
        from_date=from_date,
        to_date=to_date,
    )


async def get_mobilizon_events_with_status(
    status: list[_EventPublicationStatus],
    from_date: Optional[Arrow] = None,
    to_date: Optional[Arrow] = None,
) -> Iterable[_MobilizonEvent]:
    def _filter_event_with_status(event: Event) -> bool:
        # This computes the status client-side instead of running in the DB. It shouldn't pose a performance problem
        # in the short term, but should be moved to the query if possible.
        event_status = _compute_event_status(list(event.publications))
        return event_status in status

    return map(
        _MobilizonEvent.from_model,
        filter(_filter_event_with_status, await get_all_events(from_date, to_date)),
    )


async def get_mobilizon_events_without_publications(
    from_date: Optional[Arrow] = None, to_date: Optional[Arrow] = None,
) -> list[_MobilizonEvent]:
    return [
        _MobilizonEvent.from_model(event)
        for event in await get_events_without_publications(
            from_date=from_date, to_date=to_date
        )
    ]
