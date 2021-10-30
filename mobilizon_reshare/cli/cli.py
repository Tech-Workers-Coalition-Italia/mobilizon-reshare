import functools
from enum import Enum

import click
from arrow import Arrow
from click import pass_context

from mobilizon_reshare.cli import safe_execution
from mobilizon_reshare.cli.commands.format.format import format_event
from mobilizon_reshare.cli.commands.inspect.inspect_event import inspect_events
from mobilizon_reshare.cli.commands.start.main import main as start_main
from mobilizon_reshare.cli.commands.recap.main import main as recap_main
from mobilizon_reshare.config.publishers import publisher_names

from mobilizon_reshare.event.event import EventPublicationStatus

status_name_to_enum = {
    "waiting": EventPublicationStatus.WAITING,
    "completed": EventPublicationStatus.COMPLETED,
    "failed": EventPublicationStatus.FAILED,
    "partial": EventPublicationStatus.PARTIAL,
    "all": None,
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


class InspectTarget(Enum):
    ALL = "all"
    WAITING = "waiting"

    def __str__(self):
        return self.value


@click.group()
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


@mobilizon_reshare.command(help="Print events in the database that are in STATUS")
@from_date_option
@to_date_option
@click.argument(
    "status", type=click.Choice(list(status_name_to_enum.keys())),
)
@settings_file_option
@pass_context
def inspect(ctx, status, begin, end, settings_file):
    ctx.ensure_object(dict)
    begin = Arrow.fromdatetime(begin) if begin else None
    end = Arrow.fromdatetime(end) if end else None

    safe_execution(
        functools.partial(
            inspect_events, status_name_to_enum[status], frm=begin, to=end,
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
