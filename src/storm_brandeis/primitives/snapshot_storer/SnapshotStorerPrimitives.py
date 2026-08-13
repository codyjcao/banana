#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("SnapshotStorerPrimitives",)

from typing import Protocol


class SnapshotStorerPrimitives[Item](Protocol):
    async def save(self, item: Item) -> None: ...

    async def load(self) -> Item | None: ...