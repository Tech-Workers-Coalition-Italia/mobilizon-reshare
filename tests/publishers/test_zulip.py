import pytest

from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers import get_active_publishers
from mobilizon_reshare.publishers.coordinator import PublisherCoordinator
from mobilizon_reshare.storage.query import (
    get_publishers,
    update_publishers,
    publications_with_status,
    get_all_events,
)


@pytest.mark.asyncio
async def test_zulip_publisher(
    mocked_responses, event_model_generator, publication_model_generator
):
    settings = get_settings()
    for publisher in get_active_publishers():
        if publisher != "zulip":
            settings["publisher"][publisher]["active"] = False
    settings["publisher"]["zulip"][
        "bot_email"
    ] = "giacomotest2-bot@zulip.twc-italia.org"

    await update_publishers(["zulip"])
    publisher = await get_publishers(name="zulip")
    event = event_model_generator()
    await event.save()
    publication = publication_model_generator(
        event_id=event.id, publisher_id=publisher.id
    )
    await publication.save()

    report = PublisherCoordinator(
        list(await get_all_events())[0],
        await publications_with_status(status=PublicationStatus.WAITING),
    ).run()

    assert list(report.reports.values())[0].status == PublicationStatus.COMPLETED
