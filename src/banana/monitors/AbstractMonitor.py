#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("AbstractMonitor",)

from abc import ABC, abstractmethod


class AbstractMonitor(ABC):
    @abstractmethod
    async def monitor(self) -> None:
        raise NotImplementedError
