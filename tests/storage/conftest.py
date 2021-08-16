from datetime import timedelta
from typing import Union
from uuid import UUID

import pytest

from mobilizon_reshare.models.event import Event
from mobilizon_reshare.models.publication import PublicationStatus, Publication
from mobilizon_reshare.models.publisher import Publisher
from tests.storage import today


async def _generate_publishers(specification):

    publishers = []
    for i, publisher_name in enumerate(specification["publisher"]):
        publisher = Publisher(
            id=UUID(int=i), name=publisher_name, account_ref=f"account_ref_{i}"
        )
        publishers.append(publisher)
        await publisher.save()

    return publishers


async def _generate_events(specification):
    events = []
    if "event" in specification.keys():
        for i in range(specification["event"]):
            begin_date = today + timedelta(days=i)
            event = Event(
                id=UUID(int=i),
                name=f"event_{i}",
                description=f"desc_{i}",
                mobilizon_id=f"mobid_{i}",
                mobilizon_link=f"moblink_{i}",
                thumbnail_link=f"thumblink_{i}",
                location=f"loc_{i}",
                begin_datetime=begin_date,
                end_datetime=begin_date + timedelta(hours=2),
            )
            events.append(event)
            await event.save()
    return events


async def _generate_publications(events, publishers, specification):
    if "publications" in specification.keys():
        for i in range(len(specification["publications"])):
            publication = specification["publications"][i]
            status = publication.get("status", PublicationStatus.WAITING)
            timestamp = publication.get("timestamp", today + timedelta(hours=i))
            await Publication.create(
                id=UUID(int=i),
                status=status,
                timestamp=timestamp,
                event_id=events[publication["event_idx"]].id,
                publisher_id=publishers[publication["publisher_idx"]].id,
            )


@pytest.fixture(scope="module")
def generate_models():
    async def _generate_models(specification: dict[str, Union[int, list]]):
        publishers = await _generate_publishers(specification)
        events = await _generate_events(specification)
        await _generate_publications(events, publishers, specification)

    return _generate_models
