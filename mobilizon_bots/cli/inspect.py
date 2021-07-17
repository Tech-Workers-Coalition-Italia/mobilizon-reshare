from typing import Iterable

import click

from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.storage.query import get_all_events


def show_events(events: Iterable[MobilizonEvent]):
    click.echo_via_pager("\n".join([event.pretty() for event in events]))


async def inspect_all():
    events = await get_all_events()
    show_events(events)
