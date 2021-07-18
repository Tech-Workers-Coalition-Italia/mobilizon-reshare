from typing import Iterable

import click
from arrow import Arrow

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


def pretty(event: MobilizonEvent):
    return (
        f"{event.name}|{click.style(event.status.name, fg=status_to_color[event.status])}"
        f"|{event.mobilizon_id}|{event.publication_time['telegram'].isoformat()}"
    )


async def inspect_events(
    status: EventPublicationStatus = None, frm: Arrow = None, to: Arrow = None
):

    events = (
        await events_with_status([status], from_date=frm, to_date=to)
        if status
        else await get_all_events(from_date=frm, to_date=to)
    )

    if events:
        show_events(events)
    else:
        click.echo(f"No event found with status: {status}")
