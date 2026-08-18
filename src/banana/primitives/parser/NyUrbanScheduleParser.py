#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("NyUrbanScheduleParser",)

from collections import defaultdict
from datetime import datetime
import re
import logging

from bs4 import BeautifulSoup

from banana.models import Schedule

from .ParserPrimitives import ParserPrimitives


logger = logging.getLogger(__name__)


class NyUrbanScheduleParser(ParserPrimitives[str, Schedule.Days]):
    TIME_FORMAT = "%I:%M %p"

    @staticmethod
    def parse(raw: str) -> Schedule.Days:
        soup = BeautifulSoup(raw, "html.parser")

        slots_by_day: dict[str, list[Schedule.Day.Slot]] = defaultdict(list)

        for row in soup.select("tr"):
            checkbox = row.select_one("input[name='f_GameID']")

            if checkbox is None:
                continue

            cells = row.find_all("td")

            if len(cells) != 7:
                raise ValueError(
                    f"Expected 7 columns, got {len(cells)}"
                )

            _, date_text, gym, level, time_text, fee, availability = (
                cell.get_text(" ", strip=True)
                for cell in cells
            )

            day = NyUrbanScheduleParser._parse_day(date_text)
            start_time = NyUrbanScheduleParser._parse_start_time(
                time_text
            )

            slots_by_day[day].append(
                Schedule.Day.Slot(
                    start_time=start_time,
                    court=NyUrbanScheduleParser._parse_court(level),
                    open_slots=NyUrbanScheduleParser._parse_open_slots(
                        availability
                    ),
                )
            )
        
        logger.info(f"Parsed and found {len(slots_by_day)} days")

        return tuple(
            Schedule.Day(
                date=day,
                slots=tuple(
                    sorted(
                        slots,
                        key=lambda slot: (
                            slot.start_time,
                            slot.court,
                        ),
                    )
                ),
            )
            for day, slots in slots_by_day.items()
        )

    @staticmethod
    def _parse_day(value: str) -> str:
        # "Sun 10/25" -> "10/25"
        return value.split(maxsplit=1)[1]

    @classmethod
    def _parse_start_time(cls, value: str) -> datetime:
        start, _end = (
            part.strip()
            for part in value.split("-", maxsplit=1)
        )

        return datetime.strptime(start.upper(), cls.TIME_FORMAT)

    @staticmethod
    def _parse_court(value: str) -> int:
        match = re.search(r"Court\s+(\d+)", value, re.IGNORECASE)

        if match is None:
            raise ValueError(f"Could not determine court: {value!r}")

        return int(match.group(1))

    @staticmethod
    def _parse_open_slots(value: str) -> int | None:
        if value == "Sold Out":
            return 0

        if value == "Yes":
            return None

        match = re.fullmatch(
            r"(\d+)\s+Spaces?",
            value,
            re.IGNORECASE,
        )

        if match:
            return int(match.group(1))

        raise ValueError(f"Unknown availability value: {value!r}")