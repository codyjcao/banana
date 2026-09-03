#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("ScheduleUpdateCheck",)

from typing import Protocol
from enum import Enum
import logging

from banana.models import Schedule
from banana.protocols import AsyncRunnable
from banana.primitives import (
    SnapshotStorerPrimitives,
    DifferencerPrimitives,
    FetcherPrimitives,
    ParserPrimitives,
    PolicyPrimitives,
)


_URL = "https://www.nyurban.com/wp-admin/admin-ajax.php"


logger = logging.getLogger(__name__)


class OpenPlaySession(Enum):
    BRANDEIS_SUNDAY = {
        "action": "my_open_play_contentbb",
        "buttonid": 6,
        "gametypeid": 1,
        "filterid": 18,
    }


class ScheduleUpdateCheck(AsyncRunnable):
    class Delegate(Protocol):
        async def on_update(
            self, updates: Schedule.DayUpdates, schedule: Schedule.Days
        ): ...

        async def on_no_update(self, schedule: Schedule.Days): ...

    def __init__(
        self,
        fetcher: FetcherPrimitives[str],
        parser: ParserPrimitives[str, Schedule.Days],
        snapshot_storer: SnapshotStorerPrimitives[Schedule.Days],
        differencer: DifferencerPrimitives[Schedule.Days, Schedule.DayUpdates],
        policy: PolicyPrimitives[Schedule.DayUpdates],
        delegate: Delegate,
    ):
        self.__fetcher = fetcher
        self.__parser = parser
        self.__snapshot_storer = snapshot_storer
        self.__differencer = differencer
        self.__delegate = delegate
        self.__policy = policy

    async def run(self) -> None:
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

        if evaluation:
            logger.info("Evaluation passed... activating delegate")
            await self.__delegate.on_update(updates, parsed)
        else:
            logger.info("Policy not met, no notification generated...")
            await self.__delegate.on_no_update(parsed)
