import pytest

from mobilizon_reshare.cli.commands.list.list_event import list_events
from mobilizon_reshare.cli.commands.list.list_publication import list_publications
from mobilizon_reshare.event.event import EventPublicationStatus
from mobilizon_reshare.models.publication import PublicationStatus

spec = {
    # We need three events since recap will print only
    # future events, but the 0th event happens at today + 0.
    "event": 3,
    "publications": [
        {"event_idx": 1, "publisher_idx": 0, "status": PublicationStatus.COMPLETED},
        {"event_idx": 2, "publisher_idx": 0, "status": PublicationStatus.FAILED},
    ],
    "publisher": ["zulip"],
}


def clean_output(output):
    return list(map(lambda x: x.strip(), output.out.rstrip().split("\n")))


@pytest.mark.asyncio
async def test_list_events(capsys, generate_models):
    await generate_models(spec)
    await list_events()
    output = capsys.readouterr()
    assert clean_output(output) == [
        "event_0                    WAITING   00000000-0000-0000-0000-000000000000"
        "    2021-06-06T03:00:00+00:00    2021-06-06T05:00:00+00:00",
        "event_1                   COMPLETED  00000000-0000-0000-0000-000000000001"
        "    2021-06-07T03:00:00+00:00    2021-06-07T05:00:00+00:00",
        "event_2                    FAILED    00000000-0000-0000-0000-000000000002"
        "    2021-06-08T03:00:00+00:00    2021-06-08T05:00:00+00:00",
    ]


@pytest.mark.asyncio
async def test_list_events_with_status(capsys, generate_models):
    await generate_models(spec)
    await list_events(status=EventPublicationStatus.WAITING)
    output = capsys.readouterr()
    assert clean_output(output) == [
        "event_0                    WAITING   00000000-0000-0000-0000-000000000000"
        "    2021-06-06T03:00:00+00:00    2021-06-06T05:00:00+00:00"
    ]


@pytest.mark.asyncio
async def test_list_publications(capsys, generate_models):
    await generate_models(spec)
    await list_publications()
    output = capsys.readouterr()
    assert clean_output(output) == [
        "00000000-0000-0000-0000-000000000000    2021-06-06T03:00:00+00:00           "
        "COMPLETED    zulip       00000000-0000-0000-0000-000000000001",
        "00000000-0000-0000-0000-000000000001    2021-06-06T04:00:00+00:00           "
        "FAILED       zulip       00000000-0000-0000-0000-000000000002",
    ]


@pytest.mark.asyncio
async def test_list_publications_with_status(capsys, generate_models):
    await generate_models(spec)
    await list_publications(status=PublicationStatus.FAILED)
    output = capsys.readouterr()
    assert clean_output(output) == [
        "00000000-0000-0000-0000-000000000001    2021-06-06T04:00:00+00:00           "
        "FAILED       zulip       00000000-0000-0000-0000-000000000002"
    ]


@pytest.mark.asyncio
async def test_list_events_empty(capsys, generate_models):
    await list_events()
    output = capsys.readouterr()
    assert clean_output(output) == ["No event found"]


@pytest.mark.asyncio
async def test_list_publications_empty(capsys, generate_models):
    await list_publications()
    output = capsys.readouterr()
    assert clean_output(output) == ["No publication found"]


@pytest.mark.asyncio
async def test_list_events_empty_with_status(capsys, generate_models):
    await list_events(status=EventPublicationStatus.FAILED)
    output = capsys.readouterr()
    assert clean_output(output) == ["No event found with status: FAILED"]


@pytest.mark.asyncio
async def test_list_publications_empty_with_status(capsys, generate_models):
    await list_publications(status=PublicationStatus.FAILED)
    output = capsys.readouterr()
    assert clean_output(output) == ["No publication found with status: FAILED"]
