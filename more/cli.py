import asyncio

import click

from more.main import main


@click.group()
def more():
    pass


@more.command()
@click.option("--settings-file", type=click.Path(exists=True))
def start(settings_file):

    asyncio.run(main([settings_file] if settings_file else None))


if __name__ == "__main__":
    more()
