import uuid

import pytest

from mobilizon_reshare.cli.commands.format.format import format_event
from mobilizon_reshare.publishers.platforms.platform_mapping import (
    get_formatter_class,
    name_to_formatter_class,
)
from mobilizon_reshare.storage.query.converter import event_to_model


@pytest.mark.parametrize("publisher_name", name_to_formatter_class.keys())
@pytest.mark.asyncio
async def test_format_event(runner, event, capsys, publisher_name):
    event_model = event_to_model(event)
    await event_model.save()
    await format_event(
        event_id=str(event_model.mobilizon_id), publisher_name=publisher_name
    )

    assert (
        capsys.readouterr().out.strip()
        == get_formatter_class(publisher_name)().get_message_from_event(event).strip()
    )


@pytest.mark.asyncio
async def test_format_event_missing(runner, capsys):
    event_id = uuid.uuid4()
    await format_event(event_id=event_id, publisher_name="telegram")

    assert (
        capsys.readouterr().out.strip()
        == f"Event with mobilizon_id {event_id} not found."
    )
