from logging import DEBUG

import pytest

from mobilizon_reshare.cli.commands.recap.main import recap
from mobilizon_reshare.models.publication import PublicationStatus

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
    "publisher_class", [pytest.lazy_fixture("mock_publisher_invalid_class")]
)
@pytest.mark.asyncio
async def test_start_event_from_db(
    caplog, mock_publisher_config, mock_now, message_collector, generate_models
):
    await generate_models(spec)

    with caplog.at_level(DEBUG):
        # calling the recap command
        report = await recap()
        assert report.successful

        assert "Found 2 events to recap" in caplog.text

        recap_message = """Upcoming

event_1

event_2"""
        assert message_collector == [recap_message]
