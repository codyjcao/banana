#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("ScheduleFormatter",)

from banana.models import Schedule
from banana.protocols import StringFormatter


class ScheduleFormatter(StringFormatter[Schedule.Days]):
    @staticmethod
    def format(item: Schedule.Days) -> str:
        raise NotImplementedError