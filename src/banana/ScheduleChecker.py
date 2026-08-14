#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("ScheduleChecker",)

import logging
from typing import Callable

from banana.primitives import (
    DifferencerPrimitives,
    NotifierPrimitives,
    SnapshotStorerPrimitives,
)


logger = logging.getLogger(__name__)


class ScheduleChecker[ParsedSchedule, ScheduleUpdate]:
    def __init__(
        self,
        snapshot_storer: SnapshotStorerPrimitives[ParsedSchedule],
        differencer: DifferencerPrimitives[ParsedSchedule, ScheduleUpdate],
        notifier: NotifierPrimitives[ScheduleUpdate],
        predicate: Callable[[ScheduleUpdate], bool] = lambda _: True,
        name: str = "schedule check",
    ):
        self.__snapshot_storer = snapshot_storer
        self.__differencer = differencer
        self.__notifier = notifier
        self.__predicate = predicate
        self.__name = name

    async def check(self, parsed: ParsedSchedule) -> None:
        old = await self.__snapshot_storer.load()

        if old is not None:
            difference = self.__differencer.difference(old, parsed)

            if not difference:
                logger.info("%s found no schedule changes", self.__name)
            elif self.__predicate(difference):
                logger.info(
                    "%s found notifiable schedule changes",
                    self.__name,
                )
                await self.__notifier.notify(difference)
            else:
                logger.info(
                    "%s found changes that did not match the notification "
                    "filter",
                    self.__name,
                )
        else:
            logger.info("%s initialized snapshot baseline", self.__name)

        await self.__snapshot_storer.save(parsed)
