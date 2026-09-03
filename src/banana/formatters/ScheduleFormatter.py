#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("ScheduleFormatter",)

from banana.models import Schedule
from banana.protocols import StringFormatter


class ScheduleFormatter(StringFormatter[Schedule.Days]):
    @staticmethod
    def format(item: Schedule.Days) -> str:
        formatted_days = [
            formatted
            for day in item
            if (formatted := ScheduleFormatter.__format_day(day)) is not None
        ]

        if not formatted_days:
            return "No open slots available."

        return "\n\n".join(formatted_days)

    @staticmethod
    def __format_day(day: Schedule.Day) -> str | None:
        open_slots = [
            slot
            for slot in day.slots
            if slot.open_slots is None or slot.open_slots > 0
        ]

        if not open_slots:
            return None

        lines = [day.date] + [
            ScheduleFormatter.__format_slot(slot) for slot in open_slots
        ]
        return "\n".join(lines)

    @staticmethod
    def __format_slot(slot: Schedule.Day.Slot) -> str:
        if slot.open_slots is None:
            availability = "5+ spots open"
        elif slot.open_slots == 1:
            availability = "1 spot open"
        else:
            availability = f"{slot.open_slots} spots open"

        return (
            f"  Court {slot.court} @ {slot.start_time:%I:%M %p}: "
            f"{availability}"
        )
