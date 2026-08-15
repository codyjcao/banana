#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("ScheduleUpdateFormatter",)

from banana.models import Schedule


class ScheduleUpdateFormatter:
    @staticmethod
    def format_day_updates(day_updates: Schedule.DayUpdates) -> str:
        formatted = "\n\n".join(
            ScheduleUpdateFormatter.__format_day(day) for day in day_updates
        )
        return formatted

    @staticmethod
    def __format_day(day_update: Schedule.DayUpdate) -> str:
        lines = [day_update.date] + [
            ScheduleUpdateFormatter.__format_update(update)
            for update in day_update.updates
        ]

        return "\n".join(lines)

    @staticmethod
    def __format_update(update: Schedule.Update) -> str:
        slot = update.updated_slot

        return (
            f"  Court {slot.court} @ {slot.start_time:%I:%M %p}: "
            f"{ScheduleUpdateFormatter.\
               __format_change(update.slot_change)}"
        )

    @staticmethod
    def __format_change(change: Schedule.Update.Change) -> str:
        Change = Schedule.Update.Change

        match change.kind:
            case Change.INCREASE:
                return (
                    f"+{change.payload} spots"
                    if change.payload is not None
                    else "more spots opened up"
                )
            case Change.DECREASE:
                return (
                    f"-{change.payload} spots"
                    if change.payload is not None
                    else "fewer spots available"
                )
            case Change.NO_CHANGE:
                return "now open"
            case _:
                raise ValueError(f"{change} is not a valid change type.")