#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import os
import datetime

from storm_brandeis import (
    DualCadenceAvailabilityMonitor,
    RolloverTracker,
    ScheduleChecker,    
)
from storm_brandeis.models import Schedule
from storm_brandeis.primitives import (
    NyUrbanScheduleEmailNotifier,
    InMemorySnapshotStorer,
    NyUrbanScheduleParser,
    ScheduleDifferencer,
    RequestsFetcher,
)


async def main():
    fetcher = RequestsFetcher(
        "https://www.nyurban.com/wp-admin/admin-ajax.php",
        {
            "action": "my_open_play_contentbb",
            "buttonid": 6,
            "gametypeid": 1,
            "filterid": 18,
        }
    )
    fast_store = InMemorySnapshotStorer[Schedule.Days]()
    daily_store = InMemorySnapshotStorer[Schedule.Days]()
    parser = NyUrbanScheduleParser()
    differencer = ScheduleDifferencer()
    email_notifier_fast = NyUrbanScheduleEmailNotifier(
        sender=os.environ["EMAIL_NAME"],
        password=os.environ["EMAIL_PASSWORD"],
        recipients=["codyjcao@gmail.com"],
        subject="NYUrban Brandeis New Date Drop"
    )
    email_notifier_daily = NyUrbanScheduleEmailNotifier(
        sender=os.environ["EMAIL_NAME"],
        password=os.environ["EMAIL_PASSWORD"],
        recipients=["codyjcao@gmail.com"],
        subject="NYUrban Brandeis Daily Update"
    )

    fast_check = ScheduleChecker[Schedule.Days, Schedule.DayUpdates](
        snapshot_storer=fast_store,
        differencer=differencer,
        notifier=email_notifier_fast,
        predicate=lambda updates: any(day.new_date for day in updates),
    )

    daily_check = ScheduleChecker[Schedule.Days, Schedule.DayUpdates](
        snapshot_storer=daily_store,
        differencer=differencer,
        notifier=email_notifier_daily,
        predicate=lambda _: True,
    )

    monitor = DualCadenceAvailabilityMonitor[
        str,
        Schedule.Days,
        Schedule.DayUpdates,
    ](
        fast_check=fast_check,
        daily_check=daily_check,
        fetcher=fetcher,
        parser=parser,
        rollover_tracker=RolloverTracker(
            InMemorySnapshotStorer[datetime.datetime](),
            interval=datetime.timedelta(days=1)
        ),
        poll_interval_seconds=60*60*6
    )

    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())