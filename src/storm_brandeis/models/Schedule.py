#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from datetime import datetime


class Schedule:
    @dataclass(frozen=True)
    class Slot:
        start_time: datetime
        end_time: datetime
        court: int
        open_slots: int
        price: float

    @dataclass(frozen=True)
    class Day:
        day: datetime
        slots: tuple["Schedule.Slot", ...]

    @dataclass(frozen=True)
    class Updates:
        opening: tuple["Schedule.Day", ...]     # existing date, more slots
        closing: tuple["Schedule.Day", ...]     # existing date, fewer slots
        new_dates: tuple["Schedule.Day", ...]   # new date
