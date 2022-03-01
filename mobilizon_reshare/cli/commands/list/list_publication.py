from datetime import datetime
from typing import Iterable, Optional

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
    status: PublicationStatus = None,
    frm: Optional[datetime] = None,
    to: Optional[datetime] = None,
):

    frm = Arrow.fromdatetime(frm) if frm else None
    to = Arrow.fromdatetime(to) if to else None
    if status is None:
        publications = await get_all_publications(from_date=frm, to_date=to)
    else:
        publications = await publications_with_status(status, from_date=frm, to_date=to)

    if publications:
        show_publications(publications)
    else:
        message = (
            f"No publication found with status: {status.name}"
            if status is not None
            else "No publication found"
        )
        click.echo(message)
