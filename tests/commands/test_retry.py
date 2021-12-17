import pytest

from mobilizon_reshare.main.retry import retry


@pytest.mark.asyncio
async def test_retry_decision():
    with pytest.raises(NotImplementedError):
        await retry()


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_valid")]
)
@pytest.mark.asyncio
async def test_retry(
    event_with_failed_publication, mock_publisher_config, message_collector
):

    await retry(event_with_failed_publication.mobilizon_id)
