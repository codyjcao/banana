#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("SchedulePolicy",)

from typing import Callable
import logging
import datetime

from banana.models import Schedule

from .PolicyPrimitives import PolicyPrimitives


logger = logging.getLogger(__name__)


class SchedulePolicy(PolicyPrimitives[Schedule.DayUpdates]):
    def __init__(
        self,
        predicate: Callable[[Schedule.DayUpdates], bool] = (
            lambda x: len(x) > 0
        ),
    ):
        self.__predicate = predicate

    async def evaluate(self, item: Schedule.DayUpdates) -> bool:
        now = datetime.datetime.now().strftime("%m/%d, %H:%M")

        if self.__predicate(item):
            logger.info(
                f"Predicate success for {len(item)} day updates on"
                f" {now}"
            )
            return True
        
        logger.info(f"Predicate failed for {len(item)} updates on {now}")
        return False