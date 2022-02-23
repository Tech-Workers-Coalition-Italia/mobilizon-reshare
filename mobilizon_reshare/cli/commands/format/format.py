import click

from mobilizon_reshare.models.event import Event
from mobilizon_reshare.publishers.platforms.platform_mapping import get_formatter_class
from mobilizon_reshare.storage.query.converter import event_from_model


async def format_event(event_id, publisher_name: str):
    event = await Event.get_or_none(mobilizon_id=event_id).prefetch_related(
        "publications__publisher"
    )
    if not event:
        click.echo(f"Event with mobilizon_id {event_id} not found.")
        return
    event = event_from_model(event)
    message = get_formatter_class(publisher_name)().get_message_from_event(event)
    click.echo(message)
