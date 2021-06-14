import asyncio

import click

from mobilizon_bots.main import main


@click.group()
def mobilizon_bots():
    pass


@mobilizon_bots.command()
def start():

    asyncio.run(main())


if __name__ == "__main__":
    mobilizon_bots()
