#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from banana.checks.ScheduleCheck import ScheduleCheck

from .support import (
    MappingParser,
    RecordingScheduleDelegate,
    SequenceFetcher,
    make_day,
    make_slot,
)


def test_run_fetches_parses_and_forwards_schedule():
    schedule = (make_day("1/1", make_slot(1, 2)),)
    delegate = RecordingScheduleDelegate()
    check = ScheduleCheck(
        fetcher=SequenceFetcher(["raw schedule"]),
        parser=MappingParser({"raw schedule": schedule}),
        delegate=delegate,
    )

    asyncio.run(check.run())

    assert delegate.schedules == [schedule]
