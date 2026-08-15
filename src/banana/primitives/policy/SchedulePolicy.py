#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("SchedulePolicy",)

from typing import Callable

from banana.models import Schedule

from .PolicyPrimitives import PolicyPrimitives


class SchedulePolicy(PolicyPrimitives[Schedule.DayUpdates, str]):
    def __init__(
        self,
        formatter: Callable[[Schedule.DayUpdates], str],
        predicate: Callable[[Schedule.DayUpdates], bool] = lambda _: True,
    ):
        self.__formatter = formatter
        self.__predicate = predicate

    async def evaluate(self, item: Schedule.DayUpdates) -> str | None:
        if self.__predicate(item):
            return self.__formatter(item)
        return None