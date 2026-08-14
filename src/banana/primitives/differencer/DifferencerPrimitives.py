#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("DifferencerPrimitives",)

from typing import Protocol


class DifferencerPrimitives[Item, Difference](Protocol):
    @staticmethod
    def difference(old_item: Item, new_item: Item) -> Difference:
        ...