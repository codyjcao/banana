#!/usr/bin/env python
# -*- coding: utf-8 -*-

from banana.primitives import (
    SnapshotStorerPrimitives,
    DifferencerPrimitives,
    NotifierPrimitives,
    FetcherPrimitives,
    ParserPrimitives,
)

from .ScheduleChecker import ScheduleChecker


class AvailabilityMonitor[UnparsedSchedule, ParsedSchedule, ScheduleUpdate]:
    def __init__(
        self,
        fetcher: FetcherPrimitives[UnparsedSchedule],
        parser: ParserPrimitives[UnparsedSchedule, ParsedSchedule],
        snapshot_storer: SnapshotStorerPrimitives[ParsedSchedule],
        differencer: DifferencerPrimitives[ParsedSchedule, ScheduleUpdate],
        notifier: NotifierPrimitives[ScheduleUpdate],
    ):
        self.__fetcher = fetcher
        self.__parser = parser
        self.__schedule_check = ScheduleChecker(
            snapshot_storer, differencer, notifier, lambda _: True
        )

    async def run(self):
        unparsed = await self.__fetcher.fetch()
        parsed = self.__parser.parse(unparsed)

        await self.__schedule_check.check(parsed)
