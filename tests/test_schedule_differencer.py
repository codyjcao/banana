#!/usr/bin/env python
# -*- coding: utf-8 -*-

from banana.models import Schedule
from banana.primitives.differencer.ScheduleDifferencer import (
    ScheduleDifferencer,
)

from .support import make_day, make_slot

Change = Schedule.Update.Change


def test_unchanged_slot_produces_no_update():
    old = (make_day("1/1", make_slot(1, 3)),)
    new = (make_day("1/1", make_slot(1, 3)),)

    assert ScheduleDifferencer.difference(old, new) == ()


def test_unchanged_unspecified_slot_produces_no_update():
    old = (make_day("1/1", make_slot(1, None)),)
    new = (make_day("1/1", make_slot(1, None)),)

    assert ScheduleDifferencer.difference(old, new) == ()


def test_increase_reports_exact_delta():
    old = (make_day("1/1", make_slot(1, 2)),)
    new = (make_day("1/1", make_slot(1, 4)),)

    (day_update,) = ScheduleDifferencer.difference(old, new)
    (update,) = day_update.updates

    assert update.slot_change == Change.INCREASE(2)
    assert update.updated_slot.open_slots == 4


def test_decrease_reports_exact_magnitude():
    old = (make_day("1/1", make_slot(1, 4)),)
    new = (make_day("1/1", make_slot(1, 1)),)

    (day_update,) = ScheduleDifferencer.difference(old, new)
    (update,) = day_update.updates

    assert update.slot_change == Change.DECREASE(3)


def test_crossing_below_reporting_threshold_is_decrease_with_unknown_magnitude():
    # open_slots is None once there are >= 5 spots open; a transition
    # from None to a known int means it dropped below that threshold,
    # but the exact size of the drop isn't observable.
    old = (make_day("1/1", make_slot(1, None)),)
    new = (make_day("1/1", make_slot(1, 2)),)

    (day_update,) = ScheduleDifferencer.difference(old, new)
    (update,) = day_update.updates

    assert update.slot_change == Change.DECREASE(None)


def test_crossing_above_reporting_threshold_is_increase_with_unknown_magnitude():
    old = (make_day("1/1", make_slot(1, 2)),)
    new = (make_day("1/1", make_slot(1, None)),)

    (day_update,) = ScheduleDifferencer.difference(old, new)
    (update,) = day_update.updates

    assert update.slot_change == Change.INCREASE(None)


def test_sold_out_to_zero_produces_no_update():
    old = (make_day("1/1", make_slot(1, 0)),)
    new = (make_day("1/1", make_slot(1, 0)),)

    assert ScheduleDifferencer.difference(old, new) == ()


def test_brand_new_slot_on_known_date_is_no_change_and_not_new_date():
    old = (make_day("1/1", make_slot(1, 3)),)
    new = (make_day("1/1", make_slot(1, 3), make_slot(2, 1)),)

    (day_update,) = ScheduleDifferencer.difference(old, new)

    assert day_update.new_date is False
    (update,) = day_update.updates
    assert update.updated_slot.court == 2
    assert update.slot_change == Change.NO_CHANGE(None)


def test_brand_new_date_flags_every_slot_as_new_date():
    old = ()
    new = (make_day("1/2", make_slot(1, 3), make_slot(2, 0)),)

    (day_update,) = ScheduleDifferencer.difference(old, new)

    assert day_update.new_date is True
    assert len(day_update.updates) == 2


def test_only_changed_slots_are_included_in_a_days_updates():
    old = (make_day("1/1", make_slot(1, 3), make_slot(2, 1)),)
    new = (make_day("1/1", make_slot(1, 3), make_slot(2, 5)),)

    (day_update,) = ScheduleDifferencer.difference(old, new)

    (update,) = day_update.updates
    assert update.updated_slot.court == 2


def test_unrelated_days_are_independent():
    old = (
        make_day("1/1", make_slot(1, 2)),
        make_day("1/2", make_slot(1, 1)),
    )
    new = (
        make_day("1/1", make_slot(1, 2)),  # unchanged
        make_day("1/2", make_slot(1, 3)),  # changed
    )

    (day_update,) = ScheduleDifferencer.difference(old, new)

    assert day_update.date == "1/2"


def test_day_missing_from_new_schedule_produces_no_updates():
    old = (make_day("1/1", make_slot(1, 2)),)
    new = ()

    assert ScheduleDifferencer.difference(old, new) == ()
