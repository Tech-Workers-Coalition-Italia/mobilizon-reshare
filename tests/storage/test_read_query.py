from uuid import UUID

import pytest

from mobilizon_reshare.dataclasses.event import get_all_mobilizon_events


@pytest.mark.asyncio
async def test_get_all_events(event_generator):
    all_events = [
        event_generator(mobilizon_id=UUID(int=i), published=False) for i in range(4)
    ]
    for e in all_events:
        await e.to_model().save()

    assert list(await get_all_mobilizon_events()) == all_events
