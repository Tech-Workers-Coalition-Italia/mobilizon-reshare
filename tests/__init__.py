from datetime import datetime, timezone, timedelta

today = datetime(
    year=2021,
    month=6,
    day=6,
    hour=5,
    minute=0,
    tzinfo=timezone(timedelta(hours=2)),
)
