#!/usr/bin/env python3

"""
This module allows to customize the scheduling logic for mobilizon-reshare.

It's not intended to be part of the supported code base but just an example on how to schedule the commands of
mobilizon-reshare.
"""
import asyncio
import os
from functools import partial

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from mobilizon_reshare.cli import _safe_execution
from mobilizon_reshare.cli.commands.recap.main import recap
from mobilizon_reshare.cli.commands.start.main import start

sched = AsyncIOScheduler()

# Runs "start" from Monday to Friday every 15 mins
sched.add_job(
    partial(_safe_execution, start),
    CronTrigger.from_crontab(
        os.environ.get("MOBILIZON_RESHARE_INTERVAL", "*/15 10-18 * * 0-4")
    ),
)
# Runs "recap" once a week
sched.add_job(
    partial(_safe_execution, recap),
    CronTrigger.from_crontab(
        os.environ.get("MOBILIZON_RESHARE_RECAP_INTERVAL", "5 11 * * 0")
    ),
)
sched.start()
try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
