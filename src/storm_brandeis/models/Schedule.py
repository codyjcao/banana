#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("Schedule",)

from tagged_enum import TaggedEnum

from dataclasses import dataclass

from datetime import datetime


class Schedule:
    @dataclass(frozen=True)
    class Slot:
        start_time: datetime
        court: int
        open_slots: int | None

    @dataclass(frozen=True)
    class Day:
        date: str
        slots: tuple["Schedule.Slot", ...]

    @dataclass(frozen=True)
    class Update:
        class Change(TaggedEnum):
            INCREASE = int | None
            DECREASE = int | None
            NO_CHANGE = int | None

        updated_slot: "Schedule.Slot"
        slot_change: Change

    @dataclass(frozen=True)
    class DayUpdate:
        date: str
        updates: tuple["Schedule.Update", ...]
        new_date: bool = False
