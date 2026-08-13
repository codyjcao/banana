#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from storm_brandeis.models import Schedule

from .DifferencerPrimitives import DifferencerPrimitives


class ScheduleDifferencer(
    DifferencerPrimitives[
        tuple[Schedule.Day, ...], tuple[Schedule.DayUpdate, ...]
    ]
):
    @staticmethod
    def difference(
        old_item: tuple[Schedule.Day, ...],
        new_item: tuple[Schedule.Day, ...],
    ) -> tuple[Schedule.DayUpdate, ...]:
        old_days = ScheduleDifferencer.__tuple_days_to_dict(old_item)
        new_days = ScheduleDifferencer.__tuple_days_to_dict(new_item)

        day_updates: list[Schedule.DayUpdate] = []

        for date, new_slots in new_days.items():
            old_slots = ScheduleDifferencer.__tuple_slots_to_dict(
                old_days.get(date, ())
            )

            updates = tuple(
                update
                for slot in new_slots
                if (
                    update := ScheduleDifferencer.__slot_difference(
                        old_slots.get((slot.start_time, slot.court)), slot
                    )
                )
                is not None
            )

            if updates:
                day_updates.append(
                    Schedule.DayUpdate(
                        date=date,
                        updates=updates,
                        new_date=date not in old_days,
                    )
                )

        return tuple(day_updates)

    @staticmethod
    def __tuple_days_to_dict(
        days: tuple[Schedule.Day, ...]
    ) -> dict[str, tuple[Schedule.Slot, ...]]:
        return {_day.date: _day.slots for _day in days}

    @staticmethod
    def __tuple_slots_to_dict(
        slots: tuple[Schedule.Slot, ...]
    ) -> dict[tuple[datetime, int], Schedule.Slot]:
        return {(slot.start_time, slot.court): slot for slot in slots}

    @staticmethod
    def __slot_difference(
        old: Schedule.Slot | None, new: Schedule.Slot
    ) -> Schedule.Update | None:
        Change = Schedule.Update.Change

        if old is None:
            # No baseline to compare against, so no direction is known.
            return Schedule.Update(
                updated_slot=new, slot_change=Change.NO_CHANGE(None)
            )

        if old.open_slots == new.open_slots:
            return None

        if old.open_slots is None or new.open_slots is None:
            # open_slots is None once there are >= 5 spots open, so a
            # transition to/from None crosses that threshold without
            # revealing the exact magnitude of the change.
            slot_change = (
                Change.INCREASE(None)
                if old.open_slots is not None
                else Change.DECREASE(None)
            )
        else:
            delta = new.open_slots - old.open_slots
            slot_change = (
                Change.INCREASE(delta)
                if delta > 0
                else Change.DECREASE(abs(delta))
            )

        return Schedule.Update(updated_slot=new, slot_change=slot_change)
