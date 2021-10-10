from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.config.publishers import publisher_name_to_validators
from mobilizon_reshare.publishers import get_active_publishers
import pytest


@pytest.mark.parametrize(
    "active_publishers", [["telegram"], ["zulip"], ["telegram", "zulip"]]
)
def test_active_publishers(active_publishers):

    for publisher in publisher_name_to_validators:
        # if the publisher is in the active_publisher param, I set it to True, otherwise False
        get_settings().update(
            {f"publisher.{publisher}.active": (publisher in active_publishers)}
        )
    publishers = list(get_active_publishers())
    assert publishers == active_publishers
