#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("AsyncRunnable",)

from typing import Protocol


class AsyncRunnable(Protocol):
    async def run(self) -> None: ...