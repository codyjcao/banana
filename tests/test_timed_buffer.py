#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

import pytest

from banana.util import TimedBuffer


def test_buffer_flushes_items_in_each_time_window():
    async def scenario() -> None:
        flushed: asyncio.Queue[list[str]] = asyncio.Queue()

        async def record_flush(items: list[str]) -> None:
            await flushed.put(items)

        buffer = TimedBuffer[str](0.05, record_flush)

        await buffer.add("first")
        await asyncio.sleep(0.005)
        await buffer.add("second")

        first_batch = await asyncio.wait_for(flushed.get(), timeout=0.5)
        assert first_batch == ["first", "second"]

        await buffer.add("third")

        second_batch = await asyncio.wait_for(flushed.get(), timeout=0.5)
        assert second_batch == ["third"]

    asyncio.run(scenario())


@pytest.mark.parametrize("window_seconds", [0, -1])
def test_buffer_rejects_nonpositive_window(window_seconds):
    async def ignore(_items: list[str]) -> None:
        pass

    with pytest.raises(ValueError):
        TimedBuffer[str](window_seconds, ignore)
