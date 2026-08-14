#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import pytest

from banana.primitives.parser.NyUrbanScheduleParser import (
    NyUrbanScheduleParser,
)


def _row(
    date_text: str,
    level: str,
    time_text: str,
    fee: str,
    availability: str,
) -> str:
    return f"""
        <tr>
            <td><input type="checkbox" name="f_GameID" value="1"></td>
            <td>{date_text}</td>
            <td>Brandeis Gym</td>
            <td>{level}</td>
            <td>{time_text}</td>
            <td>{fee}</td>
            <td>{availability}</td>
        </tr>
    """


def _table(*rows: str) -> str:
    return f"<table><tbody>{''.join(rows)}</tbody></table>"


def test_rows_without_a_registration_checkbox_are_skipped():
    html = f"""
        <table><tbody>
            <tr><th>Date</th><th>Court</th></tr>
            {_row("Sun 10/25", "Court 1", "07:00 PM - 08:00 PM", "10.00", "3 Spaces")}
        </tbody></table>
    """

    days = NyUrbanScheduleParser.parse(html)

    assert len(days) == 1


def test_parses_date_court_start_time_and_open_slots():
    html = _table(
        _row("Sun 10/25", "Court 2", "07:00 PM - 08:00 PM", "10.00", "3 Spaces")
    )

    (day,) = NyUrbanScheduleParser.parse(html)
    (slot,) = day.slots

    assert day.date == "10/25"
    assert slot.court == 2
    assert slot.start_time == datetime(1900, 1, 1, 19, 0)
    assert slot.open_slots == 3


@pytest.mark.parametrize(
    ("availability", "expected"),
    [
        ("Sold Out", 0),
        ("Yes", None),
        ("3 Spaces", 3),
        ("1 Space", 1),
    ],
)
def test_open_slots_parsing(availability, expected):
    html = _table(
        _row("Sun 10/25", "Court 1", "07:00 PM - 08:00 PM", "10.00", availability)
    )

    (day,) = NyUrbanScheduleParser.parse(html)

    assert day.slots[0].open_slots == expected


def test_unknown_availability_value_raises():
    html = _table(
        _row("Sun 10/25", "Court 1", "07:00 PM - 08:00 PM", "10.00", "Maybe")
    )

    with pytest.raises(ValueError):
        NyUrbanScheduleParser.parse(html)


def test_unparseable_court_raises():
    html = _table(
        _row("Sun 10/25", "Field 1", "07:00 PM - 08:00 PM", "10.00", "Yes")
    )

    with pytest.raises(ValueError):
        NyUrbanScheduleParser.parse(html)


def test_row_with_wrong_column_count_raises():
    html = """
        <table><tbody>
            <tr>
                <td><input type="checkbox" name="f_GameID" value="1"></td>
                <td>Sun 10/25</td>
            </tr>
        </tbody></table>
    """

    with pytest.raises(ValueError):
        NyUrbanScheduleParser.parse(html)


def test_slots_on_the_same_day_are_grouped_and_sorted():
    html = _table(
        _row("Sun 10/25", "Court 2", "08:00 PM - 09:00 PM", "10.00", "Yes"),
        _row("Sun 10/25", "Court 1", "07:00 PM - 08:00 PM", "10.00", "Yes"),
        _row("Sun 10/25", "Court 1", "08:00 PM - 09:00 PM", "10.00", "Yes"),
    )

    (day,) = NyUrbanScheduleParser.parse(html)

    assert [(s.start_time.hour, s.court) for s in day.slots] == [
        (19, 1),
        (20, 1),
        (20, 2),
    ]


def test_distinct_dates_produce_distinct_days():
    html = _table(
        _row("Sun 10/25", "Court 1", "07:00 PM - 08:00 PM", "10.00", "Yes"),
        _row("Mon 10/26", "Court 1", "07:00 PM - 08:00 PM", "10.00", "Yes"),
    )

    days = NyUrbanScheduleParser.parse(html)

    assert {day.date for day in days} == {"10/25", "10/26"}
