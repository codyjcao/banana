#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import os

from dotenv import load_dotenv

from banana.models import Schedule
from banana.checks import ScheduleCheck, ScheduleUpdateCheck
from banana.formatters import ScheduleFormatter, ScheduleUpdateFormatter
from banana.primitives import (
    RequestsFetcher,
    NyUrbanScheduleParser,
    InMemorySnapshotStorer,
    ScheduleDifferencer,
    SchedulePolicy,
    EmailNotifier,
)
from banana.runners import PeriodicRunner
from banana.util import TimedBuffer


_NY_URBAN_URL = "https://www.nyurban.com/wp-admin/admin-ajax.php"
_BRANDEIS_SUNDAY_PAYLOAD = {
    "action": "my_open_play_contentbb",
    "buttonid": 6,
    "gametypeid": 1,
    "filterid": 18,
}

_DEFAULT_SCHEDULE_CHECK_INTERVAL_SECONDS = 60 * 60 * 24
_DEFAULT_SCHEDULE_UPDATE_CHECK_INTERVAL_SECONDS = 60 * 60 * 4
_DEFAULT_NOTIFICATION_BUFFER_SECONDS = 60


async def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    sender = os.environ["EMAIL_NAME"]
    password = os.environ["EMAIL_PASSWORD"]
    recipients = [
        address.strip()
        for address in os.environ["EMAIL_RECIPIENTS"].split(",")
        if address.strip()
    ]

    if not recipients:
        raise ValueError("At least one email recipient is required.")

    notifier = EmailNotifier(
        sender=sender,
        password=password,
        recipients=recipients,
        subject=os.getenv(
            "EMAIL_SUBJECT", "Brandeis Open Play Notification"
        ),
    )

    async def flush_notifications(notifications: list[str]) -> None:
        await notifier.notify("\n\n---\n\n".join(notifications))

    notification_buffer = TimedBuffer[str](
        window_seconds=float(
            os.getenv(
                "NOTIFICATION_BUFFER_SECONDS",
                _DEFAULT_NOTIFICATION_BUFFER_SECONDS,
            )
        ),
        flush=flush_notifications,
    )

    class ScheduleNotificationDelegate(
        ScheduleCheck.Delegate, ScheduleUpdateCheck.Delegate
    ):
        def __init__(self, buffer: TimedBuffer[str]):
            self.__buffer = buffer

        async def on_schedule(self, schedule: Schedule.Days) -> None:
            await self.__buffer.add(
                "Current open slots\n\n" + ScheduleFormatter.format(schedule)
            )

        async def on_update(self, updates: Schedule.DayUpdates) -> None:
            await self.__buffer.add(
                "Schedule updates\n\n"
                + ScheduleUpdateFormatter.format(updates)
            )

    fetcher = RequestsFetcher(
        url=_NY_URBAN_URL,
        payload=_BRANDEIS_SUNDAY_PAYLOAD,
    )
    parser = NyUrbanScheduleParser()
    delegate = ScheduleNotificationDelegate(notification_buffer)

    schedule_check = ScheduleCheck(
        fetcher=fetcher,
        parser=parser,
        delegate=delegate,
    )
    schedule_update_check = ScheduleUpdateCheck(
        fetcher=fetcher,
        parser=parser,
        snapshot_storer=InMemorySnapshotStorer[Schedule.Days](),
        differencer=ScheduleDifferencer(),
        policy=SchedulePolicy(),
        delegate=delegate,
    )

    schedule_runner = PeriodicRunner(
        runnable=schedule_check,
        interval_seconds=float(
            os.getenv(
                "SCHEDULE_CHECK_INTERVAL_SECONDS",
                _DEFAULT_SCHEDULE_CHECK_INTERVAL_SECONDS,
            )
        ),
    )
    schedule_update_runner = PeriodicRunner(
        runnable=schedule_update_check,
        interval_seconds=float(
            os.getenv(
                "SCHEDULE_UPDATE_CHECK_INTERVAL_SECONDS",
                _DEFAULT_SCHEDULE_UPDATE_CHECK_INTERVAL_SECONDS,
            )
        ),
    )

    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(schedule_runner.run())
        task_group.create_task(schedule_update_runner.run())


if __name__ == "__main__":
    asyncio.run(main())
