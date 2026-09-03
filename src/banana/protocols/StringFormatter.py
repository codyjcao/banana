#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("StringFormatter",)

from typing import Protocol


class StringFormatter[Item](Protocol):
    @staticmethod
    def format(item: Item) -> str: ...