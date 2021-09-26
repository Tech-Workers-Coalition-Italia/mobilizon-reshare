import functools

import click
from arrow import Arrow
from click import pass_context

from mobilizon_reshare.cli import safe_execution
from mobilizon_reshare.cli.format import format_event
from mobilizon_reshare.cli.inspect_event import inspect_events
from mobilizon_reshare.cli.main import main
from mobilizon_reshare.event.event import EventPublicationStatus

settings_file_option = click.option("--settings-file", type=click.Path(exists=True))
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


@click.group()
def mobilizon_reshare():
    pass


@mobilizon_reshare.command()
@settings_file_option
def start(settings_file):
    safe_execution(main, settings_file=settings_file)


@mobilizon_reshare.command()
@from_date_option
@to_date_option
@click.argument("target", type=str)
@settings_file_option
@pass_context
def inspect(ctx, target, begin, end, settings_file):
    ctx.ensure_object(dict)
    begin = Arrow.fromdatetime(begin) if begin else None
    end = Arrow.fromdatetime(end) if end else None
    target_to_status = {
        "waiting": EventPublicationStatus.WAITING,
        "completed": EventPublicationStatus.COMPLETED,
        "failed": EventPublicationStatus.FAILED,
        "partial": EventPublicationStatus.PARTIAL,
        "all": None,
    }
    safe_execution(
        functools.partial(
            inspect_events,
            target_to_status[target],
            frm=begin,
            to=end,
        ),
        settings_file,
    )


@mobilizon_reshare.command()
@settings_file_option
@click.argument("event-id", type=str)
@click.argument("publisher", type=str)
def format(settings_file, event_id, publisher):
    safe_execution(
        functools.partial(format_event, event_id, publisher),
        settings_file,
    )


if __name__ == "__main__":
    mobilizon_reshare()
