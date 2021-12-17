from uuid import UUID

from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.storage.query.read import get_event


async def build_retry_publications(event_mobilizon_id):
    event = await get_event(event_mobilizon_id)

    return list(
        filter(
            lambda publications: publications.status == PublicationStatus.FAILED,
            event.publications,
        )
    )


async def retry(event_id: UUID = None):
    if event_id is None:
        raise NotImplementedError(
            "Autonomous retry not implemented yet, please specify an event_id"
        )

    retry_publications = await build_retry_publications(event_id)
    assert retry_publications, retry_publications
