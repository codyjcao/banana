#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from banana.models import Schedule
from banana.monitors.AvailabilityMonitor import AvailabilityMonitor
from banana.primitives.differencer.ScheduleDifferencer import (
    ScheduleDifferencer,
)
from banana.primitives.policy.SchedulePolicy import SchedulePolicy
from banana.primitives.snapshot_storer.InMemorySnapshotStorer import (
    InMemorySnapshotStorer,
)
from banana.util.ScheduleUpdateFormatter import ScheduleUpdateFormatter

from .support import (
    IdentityParser,
    RecordingNotifier,
    SequenceFetcher,
    make_day,
    make_slot,
)


def _tick(monitor: AvailabilityMonitor) -> None:
    asyncio.run(monitor._AvailabilityMonitor__tick())


def _build_monitor(schedules, policy=None):
    notifier = RecordingNotifier[str]()
    monitor = AvailabilityMonitor(
        fetcher=SequenceFetcher(schedules),
        parser=IdentityParser(),
        snapshot_storer=InMemorySnapshotStorer(),
        differencer=ScheduleDifferencer,
        policy=policy
        or SchedulePolicy(ScheduleUpdateFormatter.format_day_updates),
        notifier=notifier,
    )
    return monitor, notifier


def test_first_run_saves_baseline_without_notifying():
    monitor, notifier = _build_monitor(
        [(make_day("1/1", make_slot(1, 2)),)]
    )

    _tick(monitor)

    assert notifier.notifications == []


def test_second_run_notifies_with_formatted_schedule_update():
    monitor, notifier = _build_monitor(
        [
            (make_day("1/1", make_slot(1, 2)),),
            (make_day("1/1", make_slot(1, 4)),),
        ]
    )

    _tick(monitor)
    _tick(monitor)

    assert notifier.notifications == [
        "1/1\n  Court 1 @ 07:00 PM: +2 spots"
    ]


def test_no_notification_is_sent_when_policy_suppresses_update():
    policy = SchedulePolicy(
        ScheduleUpdateFormatter.format_day_updates,
        predicate=lambda updates: any(day.new_date for day in updates),
    )
    monitor, notifier = _build_monitor(
        [
            (make_day("1/1", make_slot(1, 2)),),
            (make_day("1/1", make_slot(1, 4)),),
        ],
        policy=policy,
    )

    _tick(monitor)
    _tick(monitor)

    assert notifier.notifications == []


def test_policy_can_notify_on_new_dates_only():
    policy = SchedulePolicy(
        ScheduleUpdateFormatter.format_day_updates,
        predicate=lambda updates: any(day.new_date for day in updates),
    )
    monitor, notifier = _build_monitor(
        [
            (make_day("1/1", make_slot(1, 2)),),
            (
                make_day("1/1", make_slot(1, 2)),
                make_day("1/2", make_slot(1, 1)),
            ),
        ],
        policy=policy,
    )

    _tick(monitor)
    _tick(monitor)

    assert notifier.notifications == [
        "1/2\n  Court 1 @ 07:00 PM: now open"
    ]


def test_latest_schedule_is_saved_after_each_tick():
    storer = InMemorySnapshotStorer[Schedule.Days]()
    schedules = [
        (make_day("1/1", make_slot(1, 2)),),
        (make_day("1/1", make_slot(1, 4)),),
    ]
    monitor = AvailabilityMonitor(
        fetcher=SequenceFetcher(schedules),
        parser=IdentityParser(),
        snapshot_storer=storer,
        differencer=ScheduleDifferencer,
        policy=SchedulePolicy(ScheduleUpdateFormatter.format_day_updates),
        notifier=RecordingNotifier[str](),
    )

    _tick(monitor)
    _tick(monitor)

    assert asyncio.run(storer.load()) == schedules[-1]
