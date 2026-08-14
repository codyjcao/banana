#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from storm_brandeis.AvailabilityMonitor import AvailabilityMonitor
from storm_brandeis.primitives.differencer.ScheduleDifferencer import (
    ScheduleDifferencer,
)
from storm_brandeis.primitives.snapshot_storer.InMemorySnapshotStorer import (
    InMemorySnapshotStorer,
)

from .support import (
    IdentityParser,
    RecordingNotifier,
    SequenceFetcher,
    make_day,
    make_slot,
)


def _build_monitor(schedules):
    notifier = RecordingNotifier()
    monitor = AvailabilityMonitor(
        fetcher=SequenceFetcher(schedules),
        parser=IdentityParser(),
        snapshot_storer=InMemorySnapshotStorer(),
        differencer=ScheduleDifferencer,
        notifier=notifier,
    )
    return monitor, notifier


def test_first_run_saves_baseline_without_notifying():
    monitor, notifier = _build_monitor(
        [(make_day("1/1", make_slot(1, 2)),)]
    )

    asyncio.run(monitor.run())

    assert notifier.notifications == []


def test_second_run_notifies_on_any_change():
    monitor, notifier = _build_monitor(
        [
            (make_day("1/1", make_slot(1, 2)),),
            (make_day("1/1", make_slot(1, 4)),),
        ]
    )

    asyncio.run(monitor.run())
    asyncio.run(monitor.run())

    assert len(notifier.notifications) == 1


def test_run_with_no_change_does_not_notify():
    schedule = (make_day("1/1", make_slot(1, 2)),)
    monitor, notifier = _build_monitor([schedule, schedule])

    asyncio.run(monitor.run())
    asyncio.run(monitor.run())

    assert notifier.notifications == []
