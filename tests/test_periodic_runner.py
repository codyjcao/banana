#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import math

import pytest

from banana.runners import PeriodicRunner


class StopRunner(Exception):
    pass


class NoOpRunnable:
    async def run(self) -> None:
        pass


@pytest.mark.parametrize(
    "interval_seconds",
    [0, -1, math.inf, -math.inf, math.nan],
)
def test_rejects_nonpositive_or_nonfinite_intervals(interval_seconds):
    with pytest.raises(ValueError):
        PeriodicRunner(NoOpRunnable(), interval_seconds)


def test_runs_immediately_then_waits_between_repetitions():
    events = []
    sleep_count = 0

    class RecordingRunnable:
        async def run(self) -> None:
            events.append("run")

    async def scripted_sleep(seconds: float) -> None:
        nonlocal sleep_count
        sleep_count += 1
        events.append(("sleep", seconds))
        if sleep_count == 2:
            raise StopRunner

    runner = PeriodicRunner(
        RecordingRunnable(),
        interval_seconds=30,
        sleep=scripted_sleep,
    )

    with pytest.raises(StopRunner):
        asyncio.run(runner.run())

    assert events == [
        "run",
        ("sleep", 30),
        "run",
        ("sleep", 30),
    ]


def test_does_not_overlap_executions():
    active_executions = 0
    maximum_active_executions = 0
    completed_executions = 0

    class ObservedRunnable:
        async def run(self) -> None:
            nonlocal active_executions
            nonlocal maximum_active_executions
            nonlocal completed_executions

            active_executions += 1
            maximum_active_executions = max(
                maximum_active_executions, active_executions
            )
            await asyncio.sleep(0)
            active_executions -= 1
            completed_executions += 1

    async def stop_after_two_executions(_seconds: float) -> None:
        if completed_executions == 2:
            raise StopRunner

    runner = PeriodicRunner(
        ObservedRunnable(),
        interval_seconds=1,
        sleep=stop_after_two_executions,
    )

    with pytest.raises(StopRunner):
        asyncio.run(runner.run())

    assert completed_executions == 2
    assert maximum_active_executions == 1


def test_propagates_runnable_errors_without_sleeping():
    class RunnableFailure(Exception):
        pass

    class FailingRunnable:
        async def run(self) -> None:
            raise RunnableFailure

    async def unexpected_sleep(_seconds: float) -> None:
        pytest.fail("Runner slept after its runnable failed")

    runner = PeriodicRunner(
        FailingRunnable(),
        interval_seconds=1,
        sleep=unexpected_sleep,
    )

    with pytest.raises(RunnableFailure):
        asyncio.run(runner.run())


def test_propagates_cancellation():
    class CancellingRunnable:
        async def run(self) -> None:
            raise asyncio.CancelledError

    runner = PeriodicRunner(CancellingRunnable(), interval_seconds=1)

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(runner.run())
