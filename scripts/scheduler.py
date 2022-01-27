#!/usr/bin/env python3

"""
This module allows to customize the scheduling logic for mobilizon-reshare.

It's not intended to be part of the supported code base but just an example on how to schedule the commands of
mobilizon-reshare.
"""
import asyncio
from functools import partial

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from mobilizon_reshare.cli import _safe_execution
from mobilizon_reshare.cli.commands.start.main import start

sched = AsyncIOScheduler()

# Runs "start" from Monday to Friday every 15 mins
sched.add_job(
    partial(_safe_execution, start),
    "cron",
    day_of_week="mon-fri",
    minute="*/15",
    hour="10-18",
)
# Runs "recap" once a week
sched.add_job(partial(_safe_execution, start), "cron", day_of_week="mon", hour="11")
sched.start()
try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
