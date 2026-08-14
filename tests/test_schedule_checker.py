#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from banana.ScheduleChecker import ScheduleChecker
from banana.primitives.snapshot_storer.InMemorySnapshotStorer import (
    InMemorySnapshotStorer,
)

from .support import ConstantDifferencer, RecordingNotifier


def test_first_check_saves_baseline_without_notifying():
    storer = InMemorySnapshotStorer[str]()
    notifier = RecordingNotifier[str]()
    checker = ScheduleChecker(
        storer, ConstantDifferencer("some-diff"), notifier
    )

    asyncio.run(checker.check("first-snapshot"))

    assert notifier.notifications == []
    assert asyncio.run(storer.load()) == "first-snapshot"


def test_truthy_difference_notifies_by_default():
    storer = InMemorySnapshotStorer[str]("old-snapshot")
    notifier = RecordingNotifier[str]()
    checker = ScheduleChecker(
        storer, ConstantDifferencer("a-real-diff"), notifier
    )

    asyncio.run(checker.check("new-snapshot"))

    assert notifier.notifications == ["a-real-diff"]


def test_falsy_difference_never_reaches_the_predicate_or_notifier():
    storer = InMemorySnapshotStorer[str]("old-snapshot")
    notifier = RecordingNotifier[str]()
    predicate_calls = []
    checker = ScheduleChecker(
        storer,
        ConstantDifferencer[str](""),  # falsy: no actual changes
        notifier,
        predicate=lambda diff: predicate_calls.append(diff) or True,
    )

    asyncio.run(checker.check("new-snapshot"))

    assert predicate_calls == []
    assert notifier.notifications == []


def test_predicate_can_suppress_a_truthy_difference():
    storer = InMemorySnapshotStorer[str]("old-snapshot")
    notifier = RecordingNotifier[str]()
    checker = ScheduleChecker(
        storer,
        ConstantDifferencer("a-real-diff"),
        notifier,
        predicate=lambda _: False,
    )

    asyncio.run(checker.check("new-snapshot"))

    assert notifier.notifications == []


def test_snapshot_is_saved_even_when_predicate_suppresses_notification():
    storer = InMemorySnapshotStorer[str]("old-snapshot")
    checker = ScheduleChecker(
        storer,
        ConstantDifferencer("a-real-diff"),
        RecordingNotifier[str](),
        predicate=lambda _: False,
    )

    asyncio.run(checker.check("new-snapshot"))

    assert asyncio.run(storer.load()) == "new-snapshot"
