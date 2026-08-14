#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("FetcherPrimitives",)

from typing import Protocol


class FetcherPrimitives[Item](Protocol):
    async def fetch(self) -> Item: ...