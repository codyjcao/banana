#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("NotifierPrimitives",)

from typing import Protocol


class NotifierPrimitives[Item](Protocol):
    async def notify(self, item: Item) -> None: ...