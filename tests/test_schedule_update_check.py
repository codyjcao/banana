#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from banana.models import Schedule
from banana.checks.ScheduleUpdateCheck import ScheduleUpdateCheck
from banana.primitives.differencer.ScheduleDifferencer import (
    ScheduleDifferencer,
)
from banana.primitives.policy.SchedulePolicy import SchedulePolicy
from banana.primitives.snapshot_storer.InMemorySnapshotStorer import (
    InMemorySnapshotStorer,
)

from .support import (
    MappingParser,
    RecordingUpdateDelegate,
    SequenceFetcher,
    make_day,
    make_slot,
)


def _run(check: ScheduleUpdateCheck) -> None:
    asyncio.run(check.run())


def _build_monitor(schedules, policy=None, snapshot_storer=None):
    raw_values = [f"schedule-{index}" for index in range(len(schedules))]
    parser = MappingParser(dict(zip(raw_values, schedules, strict=True)))
    delegate = RecordingUpdateDelegate()
    storer = snapshot_storer or InMemorySnapshotStorer[Schedule.Days]()
    check = ScheduleUpdateCheck(
        fetcher=SequenceFetcher(raw_values),
        parser=parser,
        snapshot_storer=storer,
        differencer=ScheduleDifferencer,
        policy=policy or SchedulePolicy(),
        delegate=delegate,
    )
    return check, delegate, storer


def test_first_run_saves_baseline_without_calling_delegate():
    schedule = (make_day("1/1", make_slot(1, 2)),)
    check, delegate, storer = _build_monitor([schedule])

    _run(check)

    assert delegate.calls == []
    assert asyncio.run(storer.load()) == schedule


def test_accepted_update_is_forwarded_with_latest_schedule():
    schedules = [
        (make_day("1/1", make_slot(1, 2)),),
        (make_day("1/1", make_slot(1, 4)),),
    ]
    check, delegate, _ = _build_monitor(schedules)

    _run(check)
    _run(check)

    [(updates, schedule)] = delegate.calls
    (day_update,) = updates
    (update,) = day_update.updates
    assert schedule == schedules[-1]
    assert day_update.date == "1/1"
    assert update.updated_slot == schedules[-1][0].slots[0]
    assert update.slot_change == Schedule.Update.Change.INCREASE(2)


def test_rejected_update_does_not_call_delegate():
    policy = SchedulePolicy(predicate=lambda _: False)
    check, delegate, _ = _build_monitor(
        [
            (make_day("1/1", make_slot(1, 2)),),
            (make_day("1/1", make_slot(1, 4)),),
        ],
        policy=policy,
    )

    _run(check)
    _run(check)

    assert delegate.calls == []


def test_policy_can_select_new_dates_only():
    policy = SchedulePolicy(
        predicate=lambda updates: any(day.new_date for day in updates)
    )
    schedules = [
        (make_day("1/1", make_slot(1, 2)),),
        (
            make_day("1/1", make_slot(1, 2)),
            make_day("1/2", make_slot(1, 1)),
        ),
    ]
    check, delegate, _ = _build_monitor(schedules, policy=policy)

    _run(check)
    _run(check)

    [(updates, schedule)] = delegate.calls
    assert schedule == schedules[-1]
    assert len(updates) == 1
    assert updates[0].date == "1/2"
    assert updates[0].new_date is True


def test_latest_schedule_is_saved_after_each_run():
    storer = InMemorySnapshotStorer[Schedule.Days]()
    schedules = [
        (make_day("1/1", make_slot(1, 2)),),
        (make_day("1/1", make_slot(1, 4)),),
    ]
    check, _, _ = _build_monitor(schedules, snapshot_storer=storer)

    _run(check)
    _run(check)

    assert asyncio.run(storer.load()) == schedules[-1]
