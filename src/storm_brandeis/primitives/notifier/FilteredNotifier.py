#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("FilteredNotifier",)

from typing import Callable

from .NotifierPrimitives import NotifierPrimitives


class FilteredNotifier[Item](NotifierPrimitives[Item]):
    def __init__(
        self,
        notifier: NotifierPrimitives[Item],
        predicate: Callable[[Item], bool],
    ):
        self.__notifier = notifier
        self.__predicate = predicate

    async def notify(self, item: Item) -> None:
        if self.__predicate(item):
            await self.__notifier.notify(item)
