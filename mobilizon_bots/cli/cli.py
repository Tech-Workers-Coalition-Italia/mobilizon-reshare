import click

from mobilizon_bots.cli import safe_execution
from mobilizon_bots.cli.inspect import inspect_all
from mobilizon_bots.cli.main import main

settings_file_option = click.option("--settings-file", type=click.Path(exists=True))


@click.group()
def mobilizon_bots():
    pass


@mobilizon_bots.command()
@settings_file_option
def start(settings_file):
    safe_execution(main, settings_file=settings_file)


@mobilizon_bots.group()
def inspect():
    pass


@inspect.command()
@settings_file_option
def all(settings_file):
    safe_execution(inspect_all, settings_file)


if __name__ == "__main__":
    mobilizon_bots()
