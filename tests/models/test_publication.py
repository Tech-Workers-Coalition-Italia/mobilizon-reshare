import pytest

from datetime import datetime
from tortoise import timezone

from mobilizon_bots.models.publication import Publication, PublicationStatus


@pytest.mark.asyncio
async def test_publication_create(
    publication_model_generator, event_model_generator, publisher_model_generator
):
    event = event_model_generator()
    await event.save()
    publisher = publisher_model_generator()
    await publisher.save()
    publication_model = await publication_model_generator(
        event_id=event.id, publisher_id=publisher.id
    )
    await publication_model.save()
    publication_db = await Publication.all().first()
    assert publication_db.status == PublicationStatus.WAITING
    assert publication_db.timestamp == datetime(
        year=2021,
        month=1,
        day=1,
        hour=11,
        minute=30,
        tzinfo=timezone.get_default_timezone(),
    )
