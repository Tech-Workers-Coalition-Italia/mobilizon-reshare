import functools

import click
from arrow import Arrow
from click import pass_context

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
    "-f",
    "--settings-file",
    type=click.Path(exists=True),
    help="The path for the settings file. "
    "Overrides the one specified in the environment variables.",
)
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
event_status_option = click.option(
    "-s",
    "--status",
    type=click.Choice(list(status_name_to_enum["event"].keys())),
    default="all",
    expose_value=True,
    help="Include only events with the given STATUS.",
)
publication_status_option = click.option(
    "-s",
    "--status",
    type=click.Choice(list(status_name_to_enum["publication"].keys())),
    default="all",
    expose_value=True,
    help="Include only publications with the given STATUS.",
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
@settings_file_option
@pass_context
def mobilizon_reshare(ctx, settings_file):
    ctx.ensure_object(dict)
    ctx.obj["settings-file"] = settings_file


@mobilizon_reshare.command(help="Synchronize and publish events.")
def start(ctx):
    ctx.ensure_object(dict)
    safe_execution(start_main, settings_file=ctx.obj["settings-file"])


@mobilizon_reshare.command(help="Publish a recap of already published events.")
def recap(ctx):
    ctx.ensure_object(dict)
    safe_execution(recap_main, settings_file=ctx.obj["settings-file"])


@mobilizon_reshare.group(help="List objects in the database with different criteria.")
@from_date_option
@to_date_option
@pass_context
def inspect(ctx, begin, end):
    ctx.ensure_object(dict)
    ctx.obj["begin"] = Arrow.fromdatetime(begin) if begin else None
    ctx.obj["end"] = Arrow.fromdatetime(end) if end else None


@inspect.command(help="Query for events in the database.")
@event_status_option
@pass_context
def event(ctx, status):
    ctx.ensure_object(dict)
    safe_execution(
        functools.partial(
            inspect_events,
            status_name_to_enum["event"][status],
            frm=ctx.obj["begin"],
            to=ctx.obj["end"],
        ),
        ctx.obj["settings-file"],
    )


@inspect.command(help="Query for publications in the database.")
@publication_status_option
@pass_context
def publication(ctx, status):
    ctx.ensure_object(dict)
    safe_execution(
        functools.partial(
            inspect_publications,
            status_name_to_enum["publication"][status],
            frm=ctx.obj["begin"],
            to=ctx.obj["end"],
        ),
        ctx.obj["settings-file"],
    )


@mobilizon_reshare.command(
    help="Format and print event with EVENT-ID using the publisher's format named "
    "PUBLISHER."
)
@settings_file_option
@click.argument("event-id", type=click.UUID)
@click.argument("publisher", type=click.Choice(publisher_names))
def format(ctx, event_id, publisher):
    ctx.ensure_object(dict)
    safe_execution(
        functools.partial(format_event, event_id, publisher), ctx.obj["settings-file"],
    )


if __name__ == "__main__":
    mobilizon_reshare(obj={})
