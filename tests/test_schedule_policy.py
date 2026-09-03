#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from banana.models import Schedule
from banana.primitives.policy.SchedulePolicy import SchedulePolicy

from .support import make_slot


def _updates(*, new_date: bool = False) -> Schedule.DayUpdates:
    update = Schedule.Update(
        updated_slot=make_slot(1, 1),
        slot_change=Schedule.Update.Change.NO_CHANGE(None),
    )
    return (
        Schedule.DayUpdate(
            date="1/1",
            updates=(update,),
            new_date=new_date,
        ),
    )


def test_default_policy_accepts_nonempty_updates():
    assert asyncio.run(SchedulePolicy().evaluate(_updates())) is True


def test_default_policy_rejects_empty_updates():
    assert asyncio.run(SchedulePolicy().evaluate(())) is False


def test_custom_predicate_controls_evaluation():
    policy = SchedulePolicy(
        predicate=lambda updates: any(day.new_date for day in updates)
    )

    assert asyncio.run(policy.evaluate(_updates(new_date=True))) is True
    assert asyncio.run(policy.evaluate(_updates(new_date=False))) is False
