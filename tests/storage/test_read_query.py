import pytest

from mobilizon_reshare.storage.query.read_query import get_unpublished_events


@pytest.mark.parametrize(
    "spec, expected_output_len",
    [
        [{"event": 2, "publisher": [], "publications": []}, 2],
        [{"event": 0, "publisher": [], "publications": []}, 0],
        [
            {
                "event": 2,
                "publisher": ["zulip"],
                "publications": [{"event_idx": 0, "publisher_idx": 0}],
            },
            1,
        ],
    ],
)
@pytest.mark.asyncio
async def test_get_unpublished_events_db_only(
    spec, generate_models, expected_output_len, event_generator
):
    """Testing that with no events on Mobilizon, I retrieve all the DB unpublished events """
    await generate_models(spec)
    unpublished_events = await get_unpublished_events([])
    assert len(unpublished_events) == expected_output_len
