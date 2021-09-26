import pytest
import responses

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


api_uri = "https://zulip.twc-italia.org/api/v1/"
users_me = {
    "result": "success",
    "msg": "",
    "email": "giacomotest2-bot@zulip.twc-italia.org",
    "user_id": 217,
    "avatar_version": 1,
    "is_admin": False,
    "is_owner": False,
    "is_guest": False,
    "is_bot": True,
    "full_name": "Bot test Giacomo2",
    "timezone": "",
    "is_active": True,
    "date_joined": "2021-09-13T19:36:45.857782+00:00",
    "avatar_url": "https://secure.gravatar.com/avatar/d2d9a932bf9ff69d4e3cdf2203271500",
    "bot_type": 1,
    "bot_owner_id": 14,
    "max_message_id": 8048,
}


@pytest.fixture
def mocked_valid_response():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            api_uri + "users/me",
            json=users_me,
            status=200,
        )
        rsps.add(
            responses.POST,
            api_uri + "messages",
            json={"result": "success", "msg": "", "id": 8049},
            status=200,
        )
        yield


@pytest.fixture
def mocked_credential_error_response():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            api_uri + "users/me",
            json={"result": "error", "msg": "Your credentials are not valid!"},
            status=403,
        )
        yield


@pytest.fixture
def mocked_client_error_response():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            api_uri + "users/me",
            json=users_me,
            status=200,
        )
        rsps.add(
            responses.POST,
            api_uri + "messages",
            json={"result": "error", "msg": "Invalid request"},
            status=400,
        )
        yield


@pytest.fixture
@pytest.mark.asyncio
async def setup_db(event_model_generator, publication_model_generator):
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


@pytest.mark.asyncio
async def test_zulip_publisher(mocked_valid_response, setup_db):

    report = PublisherCoordinator(
        list(await get_all_events())[0],
        await publications_with_status(status=PublicationStatus.WAITING),
    ).run()

    assert list(report.reports.values())[0].status == PublicationStatus.COMPLETED


@pytest.mark.asyncio
async def test_zulip_publishr_failure_invalid_credentials(
    mocked_credential_error_response, setup_db
):
    report = PublisherCoordinator(
        list(await get_all_events())[0],
        await publications_with_status(status=PublicationStatus.WAITING),
    ).run()
    assert list(report.reports.values())[0].status == PublicationStatus.FAILED
    assert list(report.reports.values())[0].reason == "Invalid credentials"


@pytest.mark.asyncio
async def test_zulip_publishr_failure_client_error(
    mocked_client_error_response, setup_db
):
    report = PublisherCoordinator(
        list(await get_all_events())[0],
        await publications_with_status(status=PublicationStatus.WAITING),
    ).run()
    assert list(report.reports.values())[0].status == PublicationStatus.FAILED
    assert list(report.reports.values())[0].reason == "400 Error - Invalid request"
