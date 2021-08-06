from datetime import datetime, timezone, timedelta

from mobilizon_bots.models.publication import PublicationStatus

today = datetime(
    year=2021, month=6, day=6, hour=5, minute=0, tzinfo=timezone(timedelta(hours=2)),
)


complete_specification = {
    "event": 4,
    "publications": [
        {"event_idx": 0, "publisher_idx": 0},
        {"event_idx": 0, "publisher_idx": 1, "status": PublicationStatus.COMPLETED},
        {"event_idx": 1, "publisher_idx": 0, "status": PublicationStatus.WAITING},
        {"event_idx": 1, "publisher_idx": 1},
        {"event_idx": 2, "publisher_idx": 2, "status": PublicationStatus.FAILED},
        {"event_idx": 2, "publisher_idx": 1, "status": PublicationStatus.COMPLETED},
        {"event_idx": 3, "publisher_idx": 2, "status": PublicationStatus.COMPLETED},
    ],
}
