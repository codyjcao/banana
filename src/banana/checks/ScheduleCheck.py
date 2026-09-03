#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("ScheduleCheck",)

from typing import Protocol
import logging

from banana.models import Schedule
from banana.protocols import AsyncRunnable
from banana.primitives import (
    FetcherPrimitives,
    ParserPrimitives,
)

logger = logging.getLogger(__name__)


class ScheduleCheck(AsyncRunnable):
    class Delegate(Protocol):
        async def on_schedule(self, schedule: Schedule.Days): ...

    def __init__(
        self,
        fetcher: FetcherPrimitives[str],
        parser: ParserPrimitives[str, Schedule.Days],
        delegate: Delegate,
    ):
        self.__fetcher = fetcher
        self.__parser = parser
        self.__delegate = delegate

    async def run(self) -> None:
        logger.info("Fetching schedule...")
        unparsed = await self.__fetcher.fetch()

        logger.info("Parsing schedule...")
        parsed = self.__parser.parse(unparsed)

        logger.info("Activating delegate... 🕴🏻")
        await self.__delegate.on_schedule(parsed)
