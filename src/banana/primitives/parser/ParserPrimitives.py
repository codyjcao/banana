#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("ParserPrimitives",)

from typing import Protocol


class ParserPrimitives[UnparsedItem, ParsedItem](Protocol):
    @staticmethod
    def parse(raw: UnparsedItem) -> ParsedItem: ...