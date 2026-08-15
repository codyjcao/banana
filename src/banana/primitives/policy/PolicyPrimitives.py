#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("PolicyPrimitives",)

from typing import Protocol


class PolicyPrimitives[Item, Result](Protocol):
    async def evaluate(self, item: Item) -> Result | None: ...