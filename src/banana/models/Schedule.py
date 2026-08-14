#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("Schedule",)

from typing import NamedTuple

from datetime import datetime

from tagged_enum import TaggedEnum


class Schedule:
    class Day(NamedTuple):
        class Slot(NamedTuple):
            start_time: datetime
            court: int
            open_slots: int | None
        date: str
        slots: tuple[Slot, ...]

    class Update(NamedTuple):
        class Change(TaggedEnum):
            INCREASE = int | None
            DECREASE = int | None
            NO_CHANGE = int | None

        updated_slot: "Schedule.Day.Slot"
        slot_change: Change

    class DayUpdate(NamedTuple):
        date: str
        updates: tuple["Schedule.Update", ...]
        new_date: bool = False

    Days = tuple[Day, ...]
    DayUpdates = tuple[DayUpdate, ...]
