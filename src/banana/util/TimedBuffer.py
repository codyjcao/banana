#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("TimedBuffer",)

from typing import Callable, Awaitable
import asyncio


class TimedBuffer[T]:
    def __init__(
        self, 
        window_seconds: float,
        flush: Callable[[list[T]], Awaitable[None]],
    ):
        if window_seconds <= 0:
            raise ValueError(
                "Choose a non-negative/zero buffer window please 😒"
            )
        self.__window_seconds = window_seconds
        self.__lock = asyncio.Lock()
        self.__buffer: list[T] = []
        self.__timer_task: asyncio.Task[None] | None = None
        self.__flush = flush

    async def add(self, item: T) -> None:
        async with self.__lock:
            self.__buffer.append(item)

            if self.__timer_task is None:
                self.__timer_task = asyncio.create_task(self.__wait_to_flush())

    async def __wait_to_flush(self) -> None:
        await asyncio.sleep(self.__window_seconds)

        async with self.__lock:
            items, self.__buffer = self.__buffer, []
            self.__timer_task = None

        if items:
            await self.__flush(items)
