#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("CustomUpdateMonitor", "OpenPlaySession",)

from typing import Protocol
from enum import Enum
import logging
import asyncio

from banana.models import Schedule
from banana.primitives import (
    SnapshotStorerPrimitives,
    DifferencerPrimitives,
    NotifierPrimitives,
    FetcherPrimitives,
    ParserPrimitives,
    PolicyPrimitives,
)

from .AbstractMonitor import AbstractMonitor


_URL = "https://www.nyurban.com/wp-admin/admin-ajax.php"


logger = logging.getLogger(__name__)


class OpenPlaySession(Enum):
    BRANDEIS_SUNDAY = {
        "action": "my_open_play_contentbb",
        "buttonid": 6,
        "gametypeid": 1,
        "filterid": 18,
    }


class CustomUpdateMonitor(AbstractMonitor):
    class Delegate(Protocol):
        async def passed_evaluation(
            self, updates: Schedule.DayUpdates, schedule: Schedule.Days
        ): ...

    def __init__(
        self,
        fetcher: FetcherPrimitives[str],
        parser: ParserPrimitives[str, Schedule.Days],
        snapshot_storer: SnapshotStorerPrimitives[Schedule.Days],
        differencer: DifferencerPrimitives[Schedule.Days, Schedule.DayUpdates],
        policy: PolicyPrimitives[Schedule.DayUpdates, str],
        delegate: Delegate,
        polling_interval_seconds: int = 60 * 60 * 12,
    ):
        if polling_interval_seconds <= 60:
            raise ValueError("Please choosing a longer polling interval")
        
        self.__fetcher = fetcher
        self.__parser = parser
        self.__polling_interval = polling_interval_seconds
        self.__snapshot_storer = snapshot_storer
        self.__differencer = differencer
        self.__delegate = delegate
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
        
        updates = self.__differencer.difference(old, parsed)
        
        logger.info("Evaluating difference...")
        evaluation = await self.__policy.evaluate(updates)

        if evaluation is not None:
            logger.info("Evaluation passed... activating delegate 😎")
            await self.__delegate.passed_evaluation(updates, parsed)
        else:
            logger.info("Policy not met, no notification generated...")

    async def monitor(self):
        while True:
            await self.__tick()
            hours = self.__polling_interval//3600
            logger.info(f"Tick completed, sleeping for {hours} hours")
            await asyncio.sleep(self.__polling_interval)
