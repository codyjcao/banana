#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from banana.models import Schedule
from banana.formatters.ScheduleUpdateFormatter import ScheduleUpdateFormatter

from .support import make_slot


Change = Schedule.Update.Change


def _update(court, open_slots, change):
    return Schedule.Update(
        updated_slot=make_slot(
            court,
            open_slots,
            start_time=datetime(1900, 1, 1, 20, 30),
        ),
        slot_change=change,
    )


def test_formats_day_updates_grouped_by_date():
    day_updates = (
        Schedule.DayUpdate(
            date="1/1",
            updates=(
                _update(1, 4, Change.INCREASE(2)),
                _update(2, 1, Change.DECREASE(1)),
            ),
            new_date=False,
        ),
        Schedule.DayUpdate(
            date="1/2",
            updates=(_update(1, 1, Change.NO_CHANGE(None)),),
            new_date=True,
        ),
    )

    assert ScheduleUpdateFormatter.format(day_updates) == (
        "1/1\n"
        "  Court 1 @ 08:30 PM: +2 spots\n"
        "  Court 2 @ 08:30 PM: -1 spots\n\n"
        "1/2\n"
        "  Court 1 @ 08:30 PM: now open"
    )


def test_formats_unknown_increase_and_decrease_magnitudes():
    day_updates = (
        Schedule.DayUpdate(
            date="1/1",
            updates=(
                _update(1, None, Change.INCREASE(None)),
                _update(2, 2, Change.DECREASE(None)),
            ),
            new_date=False,
        ),
    )

    assert ScheduleUpdateFormatter.format(day_updates) == (
        "1/1\n"
        "  Court 1 @ 08:30 PM: more spots opened up\n"
        "  Court 2 @ 08:30 PM: fewer spots available"
    )
