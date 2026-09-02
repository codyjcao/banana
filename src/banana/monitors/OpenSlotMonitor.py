#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("OpenSlotMonitor",)

from typing import Protocol
import logging
import asyncio

from banana.models import Schedule
from banana.primitives import (
    FetcherPrimitives,
    PolicyPrimitives,
    ParserPrimitives,
)

from .AbstractMonitor import AbstractMonitor

logger = logging.getLogger(__name__)


class OpenSlotMonitor(AbstractMonitor):
    class Delegate(Protocol):
        async def passed_evaluation(
            self, schedule: Schedule.Days
        ): ...

    def __init__(
        self,
        fetcher: FetcherPrimitives[str],
        parser: ParserPrimitives[str, Schedule.Days],
        policy: PolicyPrimitives[Schedule.Days, str],
        delegate: Delegate,
        polling_interval_seconds: int = 60*60*12,
    ):
        if polling_interval_seconds <= 60:
            raise ValueError("Polling interval is too short...")

        self.__fetcher = fetcher
        self.__parser = parser
        self.__policy = policy
        self.__polling_interval_sceonds = polling_interval_seconds
        self.__delegate = delegate

    async def __tick(self) -> None:
        logger.info("Fetching schedule...")
        unparsed = await self.__fetcher.fetch()

        logger.info("Parsing schedule...")
        parsed = self.__parser.parse(unparsed)

        logger.info("Evaluating parsed schedule...")
        evaluation = await self.__policy.evaluate(parsed)

        if evaluation:
            logger.info("Evaluation passed... activating delegate 😎")
            await self.__delegate.passed_evaluation(parsed)


    async def monitor(self) -> None:
        while True:
            await self.__tick()
            await asyncio.sleep(self.__polling_interval_sceonds)
