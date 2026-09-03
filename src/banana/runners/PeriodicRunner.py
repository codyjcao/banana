#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("PeriodicRunner",)

from collections.abc import Awaitable, Callable
import asyncio
import logging
import math

from banana.protocols import AsyncRunnable


logger = logging.getLogger(__name__)

Sleep = Callable[[float], Awaitable[None]]


class PeriodicRunner(AsyncRunnable):
    def __init__(
        self,
        runnable: AsyncRunnable,
        interval_seconds: float,
        *,
        sleep: Sleep = asyncio.sleep,
    ):
        if not math.isfinite(interval_seconds) or interval_seconds <= 0:
            raise ValueError("Interval must be a positive, finite number 🤓.")

        self.__runnable = runnable
        self.__interval_seconds = interval_seconds
        self.__sleep = sleep

    async def run(self) -> None:
        while True:
            logger.info("Starting periodic operation...")
            await self.__runnable.run()
            logger.info(
                "Periodic operation completed; sleeping for %s seconds...",
                self.__interval_seconds,
            )
            await self.__sleep(self.__interval_seconds)
