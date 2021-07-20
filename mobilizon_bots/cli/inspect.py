from typing import Iterable

import click

from mobilizon_bots.event.event import EventPublicationStatus
from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.storage.query import get_all_events
from mobilizon_bots.storage.query import events_with_status


def show_events(events: Iterable[MobilizonEvent]):
    click.echo_via_pager("\n".join([event.pretty() for event in events]))


async def inspect_events(status: EventPublicationStatus = None):

    events = (
        await get_all_events() if status is None else await events_with_status([status])
    )

    if events:
        show_events(events)
    else:
        click.echo(f"No event found with status: {status}")
