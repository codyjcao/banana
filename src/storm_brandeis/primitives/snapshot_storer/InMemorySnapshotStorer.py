#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .SnapshotStorerPrimitives import SnapshotStorerPrimitives


class InMemorySnapshotStorer[Item](SnapshotStorerPrimitives):
    def __init__(self, snapshot: Item | None = None):
        self.__snapshot = snapshot

    async def load(self) -> Item | None:
        return self.__snapshot
    
    async def save(self, item: Item) -> None:
        self.__snapshot = item
