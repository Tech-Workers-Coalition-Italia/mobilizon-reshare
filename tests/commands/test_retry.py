import pytest

from mobilizon_reshare.main.retry import retry
from mobilizon_reshare.models.publication import PublicationStatus, Publication


@pytest.mark.asyncio
async def test_retry_decision():
    with pytest.raises(NotImplementedError):
        await retry()


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
    await retry(event_with_failed_publication.mobilizon_id)
    p = await Publication.filter(id=failed_publication.id).first()
    assert p.status == PublicationStatus.COMPLETED, p.id
    assert len(message_collector) == 1
    assert message_collector[0] == "test event|description of the event"
