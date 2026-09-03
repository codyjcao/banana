#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from banana.formatters import ScheduleFormatter

from .support import make_day, make_slot


def test_formats_only_open_slots_grouped_by_date():
    schedule = (
        make_day(
            "1/1",
            make_slot(1, 1),
            make_slot(2, 0),
            make_slot(
                3,
                None,
                start_time=datetime(1900, 1, 1, 20, 30),
            ),
        ),
        make_day("1/2", make_slot(1, 3)),
        make_day("1/3", make_slot(1, 0)),
    )

    assert ScheduleFormatter.format(schedule) == (
        "1/1\n"
        "  Court 1 @ 07:00 PM: 1 spot open\n"
        "  Court 3 @ 08:30 PM: 5+ spots open\n\n"
        "1/2\n"
        "  Court 1 @ 07:00 PM: 3 spots open"
    )


def test_formats_schedule_without_open_slots():
    schedule = (make_day("1/1", make_slot(1, 0)),)

    assert ScheduleFormatter.format(schedule) == "No open slots available."
