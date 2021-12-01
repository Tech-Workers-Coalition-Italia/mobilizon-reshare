import functools

import click
from arrow import Arrow

from mobilizon_reshare.cli import safe_execution
from mobilizon_reshare.cli.commands.format.format import format_event
from mobilizon_reshare.cli.commands.inspect.inspect_event import inspect_events
from mobilizon_reshare.cli.commands.inspect.inspect_publication import (
    inspect_publications,
)
from mobilizon_reshare.cli.commands.start.main import main as start_main
from mobilizon_reshare.cli.commands.recap.main import main as recap_main
from mobilizon_reshare.config.config import current_version
from mobilizon_reshare.config.publishers import publisher_names

from mobilizon_reshare.event.event import EventPublicationStatus
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

settings_file_option = click.option(
    "--settings-file",
    type=click.Path(exists=True),
    help="The path for the settings file. "
    "Overrides the one specified in the environment variables.",
)
from_date_option = click.option(
    "--begin",
    type=click.DateTime(),
    expose_value=True,
    help="Include only events that begin after this datetime",
)
to_date_option = click.option(
    "--end",
    type=click.DateTime(),
    expose_value=True,
    help="Include only events that begin before this datetime",
)
status_option = click.option(
    "-s",
    "--status",
    default="all",
    expose_value=True,
    help="Include only objects with the given status",
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
def mobilizon_reshare():
    pass


@mobilizon_reshare.command(help="Synchronize and publish events")
@settings_file_option
def start(settings_file):
    safe_execution(start_main, settings_file=settings_file)


@mobilizon_reshare.command(help="Publish a recap of already published events")
@settings_file_option
def recap(settings_file):
    safe_execution(recap_main, settings_file=settings_file)


@mobilizon_reshare.command(help="List objects in the database with different criteria")
@from_date_option
@to_date_option
@click.argument(
    "object",
    type=click.Choice(list(status_name_to_enum.keys())),
)
@settings_file_option
@status_option
def inspect(object, begin, end, settings_file, status):
    begin = Arrow.fromdatetime(begin) if begin else None
    end = Arrow.fromdatetime(end) if end else None

    safe_execution(
        functools.partial(
            inspect_events if object == "event" else inspect_publications,
            status_name_to_enum[object][status],
            frm=begin,
            to=end,
        ),
        settings_file,
    )


@mobilizon_reshare.command(
    help="Format and print event with mobilizon id EVENT-ID using the publisher's format named"
    "PUBLISHER"
)
@settings_file_option
@click.argument("event-id", type=click.UUID)
@click.argument("publisher", type=click.Choice(publisher_names))
def format(settings_file, event_id, publisher):
    safe_execution(
        functools.partial(format_event, event_id, publisher), settings_file,
    )


if __name__ == "__main__":
    mobilizon_reshare()
