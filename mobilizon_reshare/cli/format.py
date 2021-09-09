import click

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.event import Event
from mobilizon_reshare.publishers.coordinator import PublisherCoordinator


async def format_event(event_id, publisher):
    event = await Event.get_or_none(mobilizon_id=event_id).prefetch_related(
        "publications__publisher"
    )
    if not event:
        click.echo(f"Event with mobilizon_id {event_id} not found.")
        return
    event = MobilizonEvent.from_model(event)
    message = PublisherCoordinator.get_formatted_message(event, publisher)
    click.echo(message)
