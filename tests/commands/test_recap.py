from logging import DEBUG
from uuid import UUID

import arrow
import pytest

from mobilizon_reshare.main.recap import recap
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.storage.query.model_creation import (
    create_event_publication_models,
)


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_invalid_class")]
)
@pytest.mark.asyncio
async def test_start_event_from_db(
    caplog, mock_publisher_config, message_collector, event_generator,
):
    for i in range(2):
        event = event_generator(
            mobilizon_id=UUID(int=i), begin_date=arrow.now().shift(days=2)
        )
        event_model = event.to_model()
        await event_model.save()

        publications = await create_event_publication_models(event_model)
        for p in publications:
            p.status = PublicationStatus.COMPLETED
            await p.save()

    with caplog.at_level(DEBUG):
        # calling the recap command
        report = await recap()
        assert report.successful

        assert "Found 2 events to recap" in caplog.text

        recap_message = """Upcoming

test event

test event"""
        assert message_collector == [recap_message] * 2  # two publishers * 1 recap
