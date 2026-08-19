#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("SchedulePolicy",)

from typing import Callable
import logging
import datetime

from banana.models import Schedule

from .PolicyPrimitives import PolicyPrimitives


logger = logging.getLogger(__name__)


class SchedulePolicy(PolicyPrimitives[Schedule.DayUpdates, str]):
    def __init__(
        self,
        formatter: Callable[[Schedule.DayUpdates], str],
        predicate: Callable[[Schedule.DayUpdates], bool] = (
            lambda x: len(x) > 0
        ),
    ):
        self.__formatter = formatter
        self.__predicate = predicate

    async def evaluate(self, item: Schedule.DayUpdates) -> str | None:
        now = datetime.datetime.now().strftime("%m/%d, %H:%M")

        if self.__predicate(item):
            logger.info(
                f"Predicate success for {len(item)} day updates on"
                f" {now}"
            )
            return self.__formatter(item)
        
        logger.info(f"Predicate failed for {len(item)} updates on {now}")
        return None