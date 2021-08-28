import logging
from abc import ABC, abstractmethod
from typing import List, Optional

import arrow

from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.event.event import MobilizonEvent

logger = logging.getLogger(__name__)


class EventSelectionStrategy(ABC):
    def select(
        self,
        published_events: List[MobilizonEvent],
        unpublished_events: List[MobilizonEvent],
    ) -> Optional[MobilizonEvent]:

        if not self.is_in_publishing_window():
            return None
        return self._select(published_events, unpublished_events)

    def is_in_publishing_window(self) -> bool:
        settings = get_settings()
        window_beginning = settings["publishing"]["window"]["begin"]
        window_end = settings["publishing"]["window"]["end"]
        now_hour = arrow.now().datetime.hour
        if window_beginning <= window_end:
            return window_beginning <= now_hour < window_end
        else:
            return now_hour >= window_beginning or now_hour < window_end

    @abstractmethod
    def _select(
        self,
        published_events: List[MobilizonEvent],
        unpublished_events: List[MobilizonEvent],
    ) -> Optional[MobilizonEvent]:
        pass


class SelectNextEventStrategy(EventSelectionStrategy):
    def _select(
        self,
        published_events: List[MobilizonEvent],
        unpublished_events: List[MobilizonEvent],
    ) -> Optional[MobilizonEvent]:

        # if there are no unpublished events, there's nothing I can do
        if not unpublished_events:
            logger.debug("No event to publish.")
            return None

        first_unpublished_event = unpublished_events[0]

        # if there's no published event (first execution) I return the next in queue
        if not published_events:
            logger.debug(
                "First Execution with an available event. Picking next event in the queue."
            )
            return first_unpublished_event

        last_published_event = published_events[-1]
        now = arrow.now()
        last_published_event_most_recent_publication_time = max(
            last_published_event.publication_time.values()
        )

        assert last_published_event_most_recent_publication_time < now, (
            f"Last published event has been published in the future\n"
            f"{last_published_event_most_recent_publication_time}\n"
            f"{now}"
        )
        if (
            last_published_event_most_recent_publication_time.shift(
                minutes=get_settings()[
                    "selection.strategy_options.break_between_events_in_minutes"
                ]
            )
            > now
        ):

            logger.debug(
                "Last event was published recently. No event is going to be published."
            )
            return None

        return first_unpublished_event


STRATEGY_NAME_TO_STRATEGY_CLASS = {"next_event": SelectNextEventStrategy}


def select_event_to_publish(
    published_events: List[MobilizonEvent],
    unpublished_events: List[MobilizonEvent],
):

    strategy = STRATEGY_NAME_TO_STRATEGY_CLASS[
        get_settings()["selection"]["strategy"]
    ]()

    return strategy.select(published_events, unpublished_events)
