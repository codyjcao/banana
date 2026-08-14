#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime, timedelta

from banana.RolloverTracker import RolloverTracker
from banana.primitives.snapshot_storer.InMemorySnapshotStorer import (
    InMemorySnapshotStorer,
)


def test_no_prior_run_has_rolled_over():
    tracker = RolloverTracker(
        InMemorySnapshotStorer[datetime](), interval=timedelta(days=1)
    )

    assert asyncio.run(tracker.has_rolled_over()) is True


def test_run_within_interval_has_not_rolled_over():
    recent = datetime.now() - timedelta(hours=1)
    tracker = RolloverTracker(
        InMemorySnapshotStorer[datetime](recent), interval=timedelta(days=1)
    )

    assert asyncio.run(tracker.has_rolled_over()) is False


def test_run_older_than_interval_has_rolled_over():
    stale = datetime.now() - timedelta(days=2)
    tracker = RolloverTracker(
        InMemorySnapshotStorer[datetime](stale), interval=timedelta(days=1)
    )

    assert asyncio.run(tracker.has_rolled_over()) is True


def test_mark_run_resets_the_interval():
    stale = datetime.now() - timedelta(days=2)
    storer = InMemorySnapshotStorer[datetime](stale)
    tracker = RolloverTracker(storer, interval=timedelta(days=1))

    asyncio.run(tracker.mark_run())

    assert asyncio.run(tracker.has_rolled_over()) is False
