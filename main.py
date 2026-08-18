#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import os

from dotenv import load_dotenv

from banana.models import Schedule
from banana.monitors import NyUrbanAvailabilityMonitor
from banana.util import ScheduleUpdateFormatter
from banana.primitives import (
    InMemorySnapshotStorer,
    SchedulePolicy,
    EmailNotifier,
)

async def main():
    load_dotenv()
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    email = os.environ["EMAIL_NAME"]
    password = os.environ["EMAIL_PASSWORD"]

    if email is None or password is None:
        raise ValueError("Email or password is missing")

    notifier = EmailNotifier(
        sender=email,
        password=password,
        recipients=["codyjcao@gmail.com","qlee97@gmail.com"],
        subject="Brandeis Open Play Notification Email"
    )

    formatter = ScheduleUpdateFormatter()

    monitor = NyUrbanAvailabilityMonitor(
        snapshot_storer=InMemorySnapshotStorer[Schedule.Days](),
        policy=SchedulePolicy(formatter=formatter.format_day_updates),
        notifier=notifier,
    )

    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
