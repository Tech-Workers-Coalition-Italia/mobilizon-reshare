from typing import Iterable

import click
from arrow import Arrow

from mobilizon_reshare.models.publication import Publication, PublicationStatus
from mobilizon_reshare.storage.query.read import (
    get_all_publications,
    publications_with_status,
)

status_to_color = {
    PublicationStatus.COMPLETED: "green",
    PublicationStatus.FAILED: "red",
}


def show_publications(publications: Iterable[Publication]):
    click.echo_via_pager("\n".join(map(pretty, publications)))


def pretty(publication: Publication):
    return (
        f"{str(publication.id) : <40}{publication.timestamp.isoformat() : <36}"
        f"{click.style(publication.status.name, fg=status_to_color[publication.status]) : <22}"
        f"{publication.publisher.name : <12}{str(publication.event.id)}"
    )


async def list_publications(
    status: PublicationStatus = None, frm: Arrow = None, to: Arrow = None
):
    if status is None:
        publications = await get_all_publications(from_date=frm, to_date=to)
    else:
        publications = await publications_with_status(status, from_date=frm, to_date=to)

    if publications:
        show_publications(list(publications))
    else:
        click.echo(f"No publication found with status: {status.name}")
