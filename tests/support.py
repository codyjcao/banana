#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Reusable fakes and builders shared across the test suite.

These are hand-written stand-ins for the `*Primitives` protocols rather
than mocks: each one is a real, minimal implementation with observable
behavior, so tests assert on what actually happened instead of on how
many times a mock method was called.
"""

from datetime import datetime
from typing import Generic, TypeVar

from banana.models import Schedule

Item = TypeVar("Item")

DEFAULT_START_TIME = datetime(1900, 1, 1, 19, 0)


def make_slot(
    court: int,
    open_slots: int | None,
    start_time: datetime = DEFAULT_START_TIME,
) -> Schedule.Day.Slot:
    return Schedule.Day.Slot(
        start_time=start_time, court=court, open_slots=open_slots
    )


def make_day(date: str, *slots: Schedule.Day.Slot) -> Schedule.Day:
    return Schedule.Day(date=date, slots=tuple(slots))


class SequenceFetcher(Generic[Item]):
    """Yields items from a fixed sequence, one per call; repeats the
    last item once exhausted so tests don't need to size the sequence
    exactly to the number of ticks performed."""

    def __init__(self, items: list[Item]):
        self.__items = items
        self.__index = 0

    async def fetch(self) -> Item:
        item = self.__items[min(self.__index, len(self.__items) - 1)]
        self.__index += 1
        return item


class IdentityParser(Generic[Item]):
    """A parser for tests where the fetcher already produces the
    "parsed" shape, so no real translation is needed."""

    @staticmethod
    def parse(raw: Item) -> Item:
        return raw


class RecordingNotifier(Generic[Item]):
    def __init__(self):
        self.notifications: list[Item] = []

    async def notify(self, item: Item) -> None:
        self.notifications.append(item)


class ConstantDifferencer(Generic[Item]):
    """A differencer that ignores its inputs and always reports the
    same difference, for isolating ScheduleChecker's own control flow
    from real diffing logic."""

    def __init__(self, difference: Item):
        self.__difference = difference

    def difference(self, old_item, new_item) -> Item:
        return self.__difference


class ManualRolloverTracker:
    """A rollover tracker whose answer is set directly by the test,
    for isolating DualCadenceAvailabilityMonitor's branching from real
    interval/clock logic."""

    def __init__(self, rolled_over: bool = False):
        self.rolled_over = rolled_over
        self.mark_run_calls = 0

    async def has_rolled_over(self) -> bool:
        return self.rolled_over

    async def mark_run(self) -> None:
        self.mark_run_calls += 1
