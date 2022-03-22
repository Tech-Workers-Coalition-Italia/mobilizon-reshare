import functools

import click
from click import pass_context

from mobilizon_reshare.cli import safe_execution
from mobilizon_reshare.cli.commands.format.format import format_event
from mobilizon_reshare.cli.commands.list.list_event import list_events
from mobilizon_reshare.cli.commands.list.list_publication import list_publications
from mobilizon_reshare.cli.commands.recap.main import recap_command as recap_main
from mobilizon_reshare.cli.commands.start.main import start_command as start_main
from mobilizon_reshare.cli.commands.pull.main import pull_command as pull_main
from mobilizon_reshare.cli.commands.publish.main import publish_command as publish_main
from mobilizon_reshare.config.config import current_version
from mobilizon_reshare.config.publishers import publisher_names
from mobilizon_reshare.event.event import EventPublicationStatus
from mobilizon_reshare.cli.commands.retry.main import (
    retry_event_command,
    retry_publication_command,
)
from mobilizon_reshare.models.publication import PublicationStatus

status_name_to_enum = {
    "event": {
        "waiting": EventPublicationStatus.WAITING,
        "completed": EventPublicationStatus.COMPLETED,
        "failed": EventPublicationStatus.FAILED,
        "partial": EventPublicationStatus.PARTIAL,
        "all": None,
    },
    "publication": {
        "completed": PublicationStatus.COMPLETED,
        "failed": PublicationStatus.FAILED,
        "all": None,
    },
}
from_date_option = click.option(
    "-b",
    "--begin",
    type=click.DateTime(),
    expose_value=True,
    help="Include only events that begin after this datetime.",
)
to_date_option = click.option(
    "-e",
    "--end",
    type=click.DateTime(),
    expose_value=True,
    help="Include only events that begin before this datetime.",
)
event_status_option = click.argument(
    "status",
    type=click.Choice(list(status_name_to_enum["event"].keys())),
    default="all",
    expose_value=True,
)
publication_status_option = click.argument(
    "status",
    type=click.Choice(list(status_name_to_enum["publication"].keys())),
    default="all",
    expose_value=True,
)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(current_version())
    ctx.exit()


@click.group()
@click.option(
    "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True
)
@pass_context
def mobilizon_reshare(obj):
    pass


@mobilizon_reshare.command(
    help="Synchronize and publish events. It is equivalent to running consecutively pull and then publish."
)
@pass_context
def start(
    ctx,
):
    ctx.ensure_object(dict)
    safe_execution(
        start_main,
    )


@mobilizon_reshare.command(help="Publish a recap of already published events.")
def recap():
    safe_execution(
        recap_main,
    )


@mobilizon_reshare.command(
    help="Fetch the latest events from Mobilizon and store them."
)
def pull():
    safe_execution(
        pull_main,
    )


@mobilizon_reshare.command(help="Select an event and publish it.")
def publish():
    safe_execution(
        publish_main,
    )


@mobilizon_reshare.group(help="Operations that pertain to events")
def event():
    pass


@mobilizon_reshare.group(help="Operations that pertain to publications")
def publication():
    pass


@event.command(help="Query for events in the database.", name="list")
@event_status_option
@from_date_option
@to_date_option
def event_list(status, begin, end):

    safe_execution(
        functools.partial(
            list_events,
            status_name_to_enum["event"][status],
            frm=begin,
            to=end,
        ),
    )


@publication.command(help="Query for publications in the database.", name="list")
@publication_status_option
@from_date_option
@to_date_option
def publication_list(status, begin, end):
    safe_execution(
        functools.partial(
            list_publications,
            status_name_to_enum["publication"][status],
            frm=begin,
            to=end,
        ),
    )


@event.command(
    help="Format and print event with EVENT-ID using the publisher's format named "
    "PUBLISHER."
)
@click.argument("event-id", type=click.UUID)
@click.argument("publisher", type=click.Choice(publisher_names))
def format(
    event_id,
    publisher,
):
    safe_execution(
        functools.partial(format_event, event_id, publisher),
    )


@event.command(name="retry", help="Retries all the failed publications")
@click.argument("event-id", type=click.UUID)
def event_retry(event_id):
    safe_execution(
        functools.partial(retry_event_command, event_id),
    )


@publication.command(name="retry", help="Retries a specific publication")
@click.argument("publication-id", type=click.UUID)
def publication_retry(publication_id):
    safe_execution(
        functools.partial(retry_publication_command, publication_id),
    )


if __name__ == "__main__":
    mobilizon_reshare(obj={})
