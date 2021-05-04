from hypothesis import given
from hypothesis.strategies import lists

from tests import events


@given(
    unpublished_events=lists(events(published=True), max_size=5),
    published_events=lists(events(published=False), max_size=3),
)
def test_select_next_event_properties(unpublished_events, published_events):
    pass
