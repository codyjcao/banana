#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("DualCadenceAvailabilityMonitor",)

import asyncio

from banana.primitives import FetcherPrimitives, ParserPrimitives

from .RolloverTracker import RolloverTracker
from .ScheduleChecker import ScheduleChecker


class DualCadenceAvailabilityMonitor[
    UnparsedSchedule, ParsedSchedule, ScheduleUpdate
]:
    def __init__(
        self,
        fetcher: FetcherPrimitives[UnparsedSchedule],
        parser: ParserPrimitives[UnparsedSchedule, ParsedSchedule],
        fast_check: ScheduleChecker[ParsedSchedule, ScheduleUpdate],
        daily_check: ScheduleChecker[ParsedSchedule, ScheduleUpdate],
        rollover_tracker: RolloverTracker,
        poll_interval_seconds: float,
    ):
        self.__fetcher = fetcher
        self.__parser = parser
        self.__fast_check = fast_check
        self.__daily_check = daily_check
        self.__rollover_tracker = rollover_tracker
        self.__poll_interval_seconds = poll_interval_seconds

    async def run(self) -> None:
        while True:
            await self.__tick()
            await asyncio.sleep(self.__poll_interval_seconds)

    async def __tick(self) -> None:
        unparsed = await self.__fetcher.fetch()
        parsed = self.__parser.parse(unparsed)

        await self.__fast_check.check(parsed)

        if await self.__rollover_tracker.has_rolled_over():
            await self.__daily_check.check(parsed)
            await self.__rollover_tracker.mark_run()
