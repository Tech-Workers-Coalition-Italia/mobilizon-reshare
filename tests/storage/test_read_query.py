from uuid import UUID

import pytest

from mobilizon_reshare.storage.query.converter import event_to_model
from mobilizon_reshare.storage.query.read import get_all_events


@pytest.mark.asyncio
async def test_get_all_events(event_generator):
    all_events = [
        event_generator(mobilizon_id=UUID(int=i), published=False) for i in range(4)
    ]
    for e in all_events:
        await event_to_model(e).save()

    assert list(await get_all_events()) == all_events
