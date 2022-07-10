from logging import DEBUG

import pytest

from mobilizon_reshare.cli.commands.recap.main import recap
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.main.publish import CommandConfig

spec = {
    # We need three events since recap will print only
    # future events, but the 0th event happens at today + 0.
    "event": 3,
    "publications": [
        {"event_idx": 1, "publisher_idx": 0, "status": PublicationStatus.COMPLETED},
        {"event_idx": 2, "publisher_idx": 0, "status": PublicationStatus.COMPLETED},
    ],
    "publisher": ["zulip"],
}


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_class")]
)
@pytest.mark.asyncio
async def test_recap_event_from_db(
    caplog,
    mock_publisher_config,
    mock_now,
    message_collector,
    generate_models,
    command_config,
):
    await generate_models(spec)

    with caplog.at_level(DEBUG):
        # calling the recap command
        report = await recap(command_config)
        assert report.successful

        assert "Found 2 events to recap" in caplog.text

        recap_message = """Upcoming

event_1

event_2"""
        assert message_collector == [recap_message]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dry_run", [True, False]
)  # the behavior should be identical with and without dry-run
async def test_recap_no_event(caplog, mock_now, message_collector, dry_run):

    with caplog.at_level(DEBUG):
        # calling the recap command
        report = await recap(CommandConfig(dry_run=dry_run))
        assert report is None

        assert "Found no events" in caplog.text

        assert message_collector == []


@pytest.mark.parametrize(
    "publisher_class", [pytest.lazy_fixture("mock_publisher_invalid_class")]
)
@pytest.mark.asyncio
async def test_recap_event_dry_run(
    caplog, mock_publisher_config, mock_now, message_collector, generate_models
):
    await generate_models(spec)

    with caplog.at_level(DEBUG):
        # calling the recap command
        reports = await recap(CommandConfig(dry_run=True))
        assert reports.successful

        assert "Found 2 events to recap" in caplog.text

        assert message_collector == []

        recap_message = """Upcoming

event_1

event_2"""

        for report in reports.reports:
            assert report.published_content == recap_message
