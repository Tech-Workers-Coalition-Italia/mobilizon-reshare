import asyncio

import click

from mobilizon_bots.main import main


@click.group()
def mobilizon_bots():
    pass


@mobilizon_bots.command()
@click.option("--settings-file", type=click.Path(exists=True))
def start(settings_file):

    asyncio.run(main([settings_file] if settings_file else None))


if __name__ == "__main__":
    mobilizon_bots()
