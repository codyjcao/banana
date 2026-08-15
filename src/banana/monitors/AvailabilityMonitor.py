#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("AvailabilityMonitor",)

import asyncio

from banana.primitives import (
    SnapshotStorerPrimitives,
    DifferencerPrimitives,
    NotifierPrimitives,
    FetcherPrimitives,
    ParserPrimitives,
    PolicyPrimitives,
)


class AvailabilityMonitor[
    UnparsedSchedule, ParsedSchedule, ScheduleUpdate, Notification]:
    def __init__(
        self,
        fetcher: FetcherPrimitives[UnparsedSchedule],
        parser: ParserPrimitives[UnparsedSchedule, ParsedSchedule],
        snapshot_storer: SnapshotStorerPrimitives[ParsedSchedule],
        differencer: DifferencerPrimitives[ParsedSchedule, ScheduleUpdate],
        policy: PolicyPrimitives[ScheduleUpdate, Notification],
        notifier: NotifierPrimitives[Notification],
        polling_interval_seconds: int = 60 * 60 * 12,
    ):
        self.__fetcher = fetcher
        self.__parser = parser
        self.__polling_interval = polling_interval_seconds
        self.__snapshot_storer = snapshot_storer
        self.__differencer = differencer
        self.__notifier = notifier
        self.__policy = policy

    async def __tick(self):
        unparsed = await self.__fetcher.fetch()
        parsed = self.__parser.parse(unparsed)

        old = await self.__snapshot_storer.load()
        await self.__snapshot_storer.save(parsed)

        if old is None:
            # no benchmark exists so establish and skip this loop
            return
        
        update = self.__differencer.difference(old, parsed)
        
        notification = await self.__policy.evaluate(update)

        if notification is not None:
            await self.__notifier.notify(notification)


    async def run(self):
        while True:
            await self.__tick()
            await asyncio.sleep(self.__polling_interval)
