#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("InMemorySnapshotStorer",)

import logging

from .SnapshotStorerPrimitives import SnapshotStorerPrimitives


logger = logging.getLogger(__name__)


class InMemorySnapshotStorer[Item](SnapshotStorerPrimitives[Item]):
    def __init__(self, snapshot: Item | None = None):
        self.__snapshot = snapshot

    async def load(self) -> Item | None:
        if self.__snapshot:
            logger.info("No snapshot stored...")
        return self.__snapshot
    
    async def save(self, item: Item) -> None:
        self.__snapshot = item
