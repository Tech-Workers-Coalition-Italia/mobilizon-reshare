from uuid import UUID

import pytest

from mobilizon_reshare.storage.query.event_converter import to_model
from mobilizon_reshare.storage.query.read import get_all_events


@pytest.mark.asyncio
async def test_get_all_events(event_generator):
    all_events = [
        event_generator(mobilizon_id=UUID(int=i), published=False) for i in range(4)
    ]
    for e in all_events:
        await to_model(e).save()

    assert list(await get_all_events()) == all_events
