#!/usr/bin/env python
# -*- coding: utf-8 -*-

from storm_brandeis.primitives import (
    SnapshotStorerPrimitives,
    DifferencerPrimitives,
    NotifierPrimitives,
    FetcherPrimitives,
    ParserPrimitives,
)

from .ScheduleCheck import ScheduleCheck


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
        self.__schedule_check = ScheduleCheck(
            snapshot_storer, differencer, notifier
        )

    async def run(self):
        unparsed = await self.__fetcher.fetch()
        parsed = self.__parser.parse(unparsed)

        await self.__schedule_check.check(parsed)
