from datetime import datetime
from typing import Iterable, Optional

import click
from arrow import Arrow

from mobilizon_reshare.dataclasses import MobilizonEvent
from mobilizon_reshare.dataclasses.event import (
    _EventPublicationStatus,
    get_all_mobilizon_events,
    get_published_events,
    get_mobilizon_events_with_status,
    get_mobilizon_events_without_publications,
)
from mobilizon_reshare.event.event_selection_strategies import select_unpublished_events

status_to_color = {
    _EventPublicationStatus.COMPLETED: "green",
    _EventPublicationStatus.FAILED: "red",
    _EventPublicationStatus.PARTIAL: "yellow",
    _EventPublicationStatus.WAITING: "white",
}


def show_events(events: Iterable[MobilizonEvent]):
    click.echo_via_pager("\n".join(map(pretty, events)))


def pretty(event: MobilizonEvent):
    return (
        f"{event.name : ^40}{click.style(event.status.name, fg=status_to_color[event.status]) : ^22}"
        f"{str(event.mobilizon_id) : <40}"
        f"{event.begin_datetime.to('local').isoformat() : <29}"
        f"{event.end_datetime.to('local').isoformat()}"
    )


async def list_unpublished_events(frm: Arrow = None, to: Arrow = None):
    return select_unpublished_events(
        list(await get_published_events(from_date=frm, to_date=to)),
        list(
            await get_mobilizon_events_without_publications(from_date=frm, to_date=to)
        ),
    )


async def list_events(
    status: Optional[_EventPublicationStatus] = None,
    frm: Optional[datetime] = None,
    to: Optional[datetime] = None,
):

    frm = Arrow.fromdatetime(frm) if frm else None
    to = Arrow.fromdatetime(to) if to else None
    if status is None:
        events = await get_all_mobilizon_events(from_date=frm, to_date=to)
    elif status == _EventPublicationStatus.WAITING:
        events = await list_unpublished_events(frm=frm, to=to)
    else:
        events = await get_mobilizon_events_with_status(
            [status], from_date=frm, to_date=to
        )
    events = list(events)
    if events:
        show_events(events)
    else:
        message = (
            f"No event found with status: {status.name}"
            if status is not None
            else "No event found"
        )
        click.echo(message)
