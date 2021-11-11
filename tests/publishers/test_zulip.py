from functools import partial

import pytest
import requests
import responses

from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers import get_active_publishers
from mobilizon_reshare.publishers.abstract import EventPublication
from mobilizon_reshare.publishers.coordinator import PublisherCoordinator
from mobilizon_reshare.publishers.exceptions import (
    InvalidEvent,
    InvalidResponse,
    ZulipError,
    InvalidMessage,
)
from mobilizon_reshare.publishers.platforms.zulip import ZulipFormatter, ZulipPublisher
from mobilizon_reshare.storage.query.save_query import update_publishers
from mobilizon_reshare.storage.query.model_creation import (
    create_event_publication_models,
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
            responses.GET, api_uri + "users/me", json=users_me, status=200,
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
            responses.GET, api_uri + "users/me", json=users_me, status=200,
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
    settings["publisher"]["zulip"][
        "instance"
    ] = "https://zulip.twc-italia.org"

    await update_publishers(["zulip"])
    publisher = await Publisher.filter(name="zulip").first()
    event = event_model_generator()
    await event.save()
    publication = publication_model_generator(
        event_id=event.id, publisher_id=publisher.id
    )
    await publication.save()


@pytest.fixture
@pytest.mark.asyncio
async def publication_models(event):
    await event.to_model().save()
    publication_models = await create_event_publication_models(event)
    return publication_models


@pytest.mark.asyncio
async def test_zulip_publisher(
    mocked_valid_response, setup_db, event, publication_models
):

    report = PublisherCoordinator(
        list(map(partial(EventPublication.from_orm, event=event), publication_models,))
    ).run()

    assert report.reports[0].status == PublicationStatus.COMPLETED


@pytest.mark.asyncio
async def test_zulip_publishr_failure_invalid_credentials(
    mocked_credential_error_response, setup_db, event, publication_models
):
    report = PublisherCoordinator(
        list(map(partial(EventPublication.from_orm, event=event), publication_models))
    ).run()
    assert report.reports[0].status == PublicationStatus.FAILED
    assert report.reports[0].reason == "403 Error - Your credentials are not valid!"


@pytest.mark.asyncio
async def test_zulip_publisher_failure_client_error(
    mocked_client_error_response, setup_db, event, publication_models
):
    report = PublisherCoordinator(
        list(map(partial(EventPublication.from_orm, event=event), publication_models))
    ).run()
    assert report.reports[0].status == PublicationStatus.FAILED
    assert report.reports[0].reason == "400 Error - Invalid request"


def test_event_validation(event):
    event.description = None
    with pytest.raises(InvalidEvent):
        ZulipFormatter().validate_event(event)


def test_message_length_success(event):
    message = "a" * 500
    event.description = message
    assert (
        ZulipFormatter().validate_message(
            ZulipFormatter().get_message_from_event(event)
        )
        is None
    )


def test_message_length_failure(event):
    message = "a" * 10000
    event.description = message
    with pytest.raises(InvalidMessage):
        ZulipFormatter().validate_message(
            ZulipFormatter().get_message_from_event(event)
        )


def test_validate_response():
    response = requests.Response()
    response.status_code = 200
    response._content = b"""{"result":"ok"}"""
    ZulipPublisher()._validate_response(response)


def test_validate_response_invalid_json():
    response = requests.Response()
    response.status_code = 200
    response._content = b"""{"osxsa"""
    with pytest.raises(InvalidResponse) as e:
        ZulipPublisher()._validate_response(response)

    e.match("json")


def test_validate_response_invalid_request():
    response = requests.Response()
    response.status_code = 400
    response._content = b"""{"result":"error", "msg":"wrong request"}"""
    with pytest.raises(ZulipError) as e:

        ZulipPublisher()._validate_response(response)

    e.match("wrong request")
