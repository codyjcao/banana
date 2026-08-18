#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("AvailabilityMonitor",)

import asyncio
import logging

from banana.primitives import (
    SnapshotStorerPrimitives,
    DifferencerPrimitives,
    NotifierPrimitives,
    FetcherPrimitives,
    ParserPrimitives,
    PolicyPrimitives,
)


logger = logging.getLogger(__name__)


class AvailabilityMonitor[
    UnparsedSchedule, ParsedSchedule, ScheduleUpdate, Notification
]:
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

        logger.info("Loading snapshot...")
        old = await self.__snapshot_storer.load()
        logger.info("Snapshot loaded...")

        logger.info("Saving new snapshot...")
        await self.__snapshot_storer.save(parsed)
        logger.info("Snapshot saved...")

        if old is None:
            logger.info("No old snapshot exists, establishing baseline...")
            return
        
        update = self.__differencer.difference(old, parsed)
        
        logger.info("Evaluating difference...")
        notification = await self.__policy.evaluate(update)

        if notification is not None:
            logger.info("Sending notification...")
            await self.__notifier.notify(notification)


    async def run(self):
        while True:
            await self.__tick()
            await asyncio.sleep(self.__polling_interval)
