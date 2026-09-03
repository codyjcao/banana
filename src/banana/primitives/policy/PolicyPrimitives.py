#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("PolicyPrimitives",)

from typing import Protocol


class PolicyPrimitives[Item](Protocol):
    async def evaluate(self, item: Item) -> bool: ...