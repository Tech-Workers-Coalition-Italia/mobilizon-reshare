import uuid
from logging import INFO

import pytest

from mobilizon_reshare.main.retry import retry_event
from mobilizon_reshare.models.publication import PublicationStatus, Publication


@pytest.mark.asyncio
async def test_retry_decision():
    with pytest.raises(NotImplementedError):
        await retry_event()


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
async def test_retry(
    event_with_failed_publication,
    mock_publisher_config,
    message_collector,
    failed_publication,
):
    assert failed_publication.status == PublicationStatus.FAILED
    await retry_event(event_with_failed_publication.mobilizon_id)
    p = await Publication.filter(id=failed_publication.id).first()
    assert p.status == PublicationStatus.COMPLETED, p.id
    assert len(message_collector) == 1
    assert message_collector[0] == "test event|description of the event"


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
async def test_retry_no_publications(
    stored_event, mock_publisher_config, message_collector, caplog
):
    with caplog.at_level(INFO):
        await retry_event(stored_event.mobilizon_id)
        assert "No failed publications found" in caplog.text
    assert len(message_collector) == 0


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
async def test_retry_missing_event(mock_publisher_config, message_collector, caplog):
    event_id = uuid.uuid4()
    with caplog.at_level(INFO):
        await retry_event(event_id)
        assert f"Event with id {event_id} not found" in caplog.text

    assert len(message_collector) == 0


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
async def test_retry_mixed_publications(
    event_with_failed_publication,
    mock_publisher_config,
    message_collector,
    failed_publication,
    publication_model_generator,
):
    p = publication_model_generator(
        event_id=event_with_failed_publication.id,
        status=PublicationStatus.COMPLETED,
        publisher_id=mock_publisher_config.id,
    )
    await p.save()

    assert failed_publication.status == PublicationStatus.FAILED
    await retry_event(event_with_failed_publication.mobilizon_id)
    p = await Publication.filter(id=failed_publication.id).first()
    assert p.status == PublicationStatus.COMPLETED, p.id
    assert len(message_collector) == 1
    assert message_collector[0] == "test event|description of the event"
