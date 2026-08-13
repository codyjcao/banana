#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("DailyRolloverTracker",)

from datetime import date

from storm_brandeis.primitives import SnapshotStorerPrimitives


class DailyRolloverTracker:
    def __init__(self, storer: SnapshotStorerPrimitives[date]):
        self.__storer = storer

    async def has_rolled_over(self) -> bool:
        last_run = await self.__storer.load()

        return last_run is None or last_run != date.today()

    async def mark_run(self) -> None:
        await self.__storer.save(date.today())
