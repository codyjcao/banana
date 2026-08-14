#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from banana.DualCadenceAvailabilityMonitor import (
    DualCadenceAvailabilityMonitor,
)
from banana.ScheduleChecker import ScheduleChecker
from banana.models import Schedule
from banana.primitives.differencer.ScheduleDifferencer import (
    ScheduleDifferencer,
)
from banana.primitives.snapshot_storer.InMemorySnapshotStorer import (
    InMemorySnapshotStorer,
)

from .support import (
    IdentityParser,
    ManualRolloverTracker,
    RecordingNotifier,
    SequenceFetcher,
    make_day,
    make_slot,
)


def _build_monitor(rollover_tracker, schedules):
    fast_notifier = RecordingNotifier()
    daily_notifier = RecordingNotifier()

    fast_check = ScheduleChecker(
        InMemorySnapshotStorer(),
        ScheduleDifferencer,
        fast_notifier,
        predicate=lambda updates: any(d.new_date for d in updates),
    )
    daily_check = ScheduleChecker(
        InMemorySnapshotStorer(), ScheduleDifferencer, daily_notifier
    )

    monitor = DualCadenceAvailabilityMonitor(
        fetcher=SequenceFetcher(schedules),
        parser=IdentityParser(),
        fast_check=fast_check,
        daily_check=daily_check,
        rollover_tracker=rollover_tracker,
        poll_interval_seconds=0,
    )

    return monitor, fast_notifier, daily_notifier


async def _tick(monitor: DualCadenceAvailabilityMonitor) -> None:
    await monitor._DualCadenceAvailabilityMonitor__tick()


def test_daily_check_is_skipped_without_a_rollover():
    tracker = ManualRolloverTracker(rolled_over=False)
    schedules = [
        (make_day("1/1", make_slot(1, 2)),),
        (make_day("1/1", make_slot(1, 4)),),  # spot change only
    ]
    monitor, fast_notifier, daily_notifier = _build_monitor(
        tracker, schedules
    )

    asyncio.run(_tick(monitor))
    asyncio.run(_tick(monitor))

    assert daily_notifier.notifications == []
    assert tracker.mark_run_calls == 0


def test_daily_check_runs_and_marks_rollover_when_due():
    tracker = ManualRolloverTracker(rolled_over=True)
    schedules = [
        (make_day("1/1", make_slot(1, 2)),),
        (make_day("1/1", make_slot(1, 4)),),  # spot change
    ]
    monitor, _, daily_notifier = _build_monitor(tracker, schedules)

    asyncio.run(_tick(monitor))  # establishes daily baseline, no diff yet
    asyncio.run(_tick(monitor))  # real change now visible

    assert len(daily_notifier.notifications) == 1
    assert tracker.mark_run_calls == 2


def test_fast_check_only_notifies_on_new_dates_not_spot_changes():
    tracker = ManualRolloverTracker(rolled_over=False)
    schedules = [
        (make_day("1/1", make_slot(1, 2)),),
        (make_day("1/1", make_slot(1, 4)),),  # spot change only
        (
            make_day("1/1", make_slot(1, 4)),
            make_day("1/2", make_slot(1, 1)),  # new date
        ),
    ]
    monitor, fast_notifier, _ = _build_monitor(tracker, schedules)

    asyncio.run(_tick(monitor))
    asyncio.run(_tick(monitor))

    assert fast_notifier.notifications == []

    asyncio.run(_tick(monitor))

    assert len(fast_notifier.notifications) == 1
    (day_update,) = fast_notifier.notifications[0]
    assert day_update.date == "1/2"
    assert day_update.new_date is True


def test_fast_and_daily_checks_use_independent_baselines():
    Change = Schedule.Update.Change
    tracker = ManualRolloverTracker(rolled_over=True)
    fast_notifier = RecordingNotifier()
    daily_notifier = RecordingNotifier()

    # No new-dates-only filter here: both checks notify on any change,
    # so the comparison below isolates what each check's baseline is.
    fast_check = ScheduleChecker(
        InMemorySnapshotStorer(), ScheduleDifferencer, fast_notifier
    )
    daily_check = ScheduleChecker(
        InMemorySnapshotStorer(), ScheduleDifferencer, daily_notifier
    )

    schedules = [
        (make_day("1/1", make_slot(1, 2)),),  # tick 1: baseline for both
        (make_day("1/1", make_slot(1, 4)),),  # tick 2: fast-only update
        (make_day("1/1", make_slot(1, 7)),),  # tick 3: both compare here
    ]
    monitor = DualCadenceAvailabilityMonitor(
        fetcher=SequenceFetcher(schedules),
        parser=IdentityParser(),
        fast_check=fast_check,
        daily_check=daily_check,
        rollover_tracker=tracker,
        poll_interval_seconds=0,
    )

    asyncio.run(_tick(monitor))  # both baselines set to tick 1's snapshot

    tracker.rolled_over = False
    asyncio.run(_tick(monitor))  # only the fast check's baseline advances

    tracker.rolled_over = True
    asyncio.run(_tick(monitor))  # fast diffs from tick 2; daily from tick 1

    (fast_day_update,) = fast_notifier.notifications[-1]
    (fast_update,) = fast_day_update.updates
    assert fast_update.slot_change == Change.INCREASE(3)  # 7 - 4

    (daily_day_update,) = daily_notifier.notifications[-1]
    (daily_update,) = daily_day_update.updates
    assert daily_update.slot_change == Change.INCREASE(5)  # 7 - 2
