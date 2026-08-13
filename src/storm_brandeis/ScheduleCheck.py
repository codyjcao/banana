#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("ScheduleCheck",)

from storm_brandeis.primitives import (
    DifferencerPrimitives,
    NotifierPrimitives,
    SnapshotStorerPrimitives,
)


class ScheduleCheck[ParsedSchedule, ScheduleUpdate]:
    def __init__(
        self,
        snapshot_storer: SnapshotStorerPrimitives[ParsedSchedule],
        differencer: DifferencerPrimitives[ParsedSchedule, ScheduleUpdate],
        notifier: NotifierPrimitives[ScheduleUpdate],
    ):
        self.__snapshot_storer = snapshot_storer
        self.__differencer = differencer
        self.__notifier = notifier

    async def check(self, parsed: ParsedSchedule) -> None:
        old = await self.__snapshot_storer.load()

        if old is not None:
            difference = self.__differencer.difference(old, parsed)

            if difference:
                await self.__notifier.notify(difference)

        await self.__snapshot_storer.save(parsed)
