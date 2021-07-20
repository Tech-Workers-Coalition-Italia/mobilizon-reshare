from typing import Iterable

import click

from mobilizon_bots.event.event import EventPublicationStatus
from mobilizon_bots.event.event import MobilizonEvent
from mobilizon_bots.storage.query import get_all_events
from mobilizon_bots.storage.query import events_with_status


status_to_color = {
    EventPublicationStatus.COMPLETED: "green",
    EventPublicationStatus.FAILED: "red",
    EventPublicationStatus.PARTIAL: "yellow",
    EventPublicationStatus.WAITING: "white",
}


def show_events(events: Iterable[MobilizonEvent]):
    click.echo_via_pager("\n".join(map(pretty, events)))


def pretty(event):

    return (
        f"{event.name}|{click.style(event.status.name, fg=status_to_color[event.status])}"
        f"|{event.mobilizon_id}"
    )


async def inspect_events(status: EventPublicationStatus = None):

    # TODO: broken, don't merge. events_with_status expects a publication status and it doesn't work as intended here
    events = (
        await get_all_events() if status is None else await events_with_status([status])
    )

    if events:
        show_events(events)
    else:
        click.echo(f"No event found with status: {status}")
