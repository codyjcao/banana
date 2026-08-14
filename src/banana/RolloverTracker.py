#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("RolloverTracker",)


import datetime
from banana.primitives import SnapshotStorerPrimitives


class RolloverTracker:
    def __init__(
        self,
        storer: SnapshotStorerPrimitives[datetime.datetime],
        interval: datetime.timedelta
    ):
        self.__storer = storer
        self.__interval = interval

    async def has_rolled_over(self) -> bool:
        last_run = await self.__storer.load()

        return (last_run is None
                or (datetime.datetime.now() - last_run) > self.__interval)

    async def mark_run(self) -> None:
        await self.__storer.save(datetime.datetime.now())
