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


class MappingParser(Generic[Item]):
    def __init__(self, parsed_by_raw_value: dict[str, Item]):
        self.__parsed_by_raw_value = parsed_by_raw_value

    def parse(self, raw: str) -> Item:
        return self.__parsed_by_raw_value[raw]


class RecordingUpdateDelegate:
    def __init__(self):
        self.calls: list[tuple[Schedule.DayUpdates, Schedule.Days]] = []
        self.no_update_schedules: list[Schedule.Days] = []

    async def on_update(
        self, updates: Schedule.DayUpdates, schedule: Schedule.Days
    ) -> None:
        self.calls.append((updates, schedule))

    async def on_no_update(self, schedule: Schedule.Days) -> None:
        self.no_update_schedules.append(schedule)


class RecordingScheduleDelegate:
    def __init__(self):
        self.schedules: list[Schedule.Days] = []

    async def on_schedule(self, schedule: Schedule.Days) -> None:
        self.schedules.append(schedule)
