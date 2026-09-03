#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("RequestsFetcher",)

from typing import Any
import asyncio
import logging
import time

import requests

from .FetcherPrimitives import FetcherPrimitives


logger = logging.getLogger(__name__)


class RequestsFetcher(FetcherPrimitives[str]):
    def __init__(
        self,
        url: str,
        payload: dict[str, Any],
        timeout: int = 15,
        cache_expiry: int = 60 * 15,
    ):
        self.__url = url
        self.__payload = payload.copy()
        self.__timeout = timeout
        self.__last_fetched_time: float | None = None
        self.__last_fetched_payload: str | None = None
        self.__cache_expiry = cache_expiry
        self.__lock = asyncio.Lock()

    async def fetch(self) -> str:
        if self.__cache_is_valid():
            assert self.__last_fetched_payload is not None
            return self.__last_fetched_payload

        async with self.__lock:
            if self.__cache_is_valid():
                assert self.__last_fetched_payload is not None
                return self.__last_fetched_payload

            response = await asyncio.to_thread(
                requests.post,
                self.__url,
                data=self.__payload,
                timeout=self.__timeout,
            )
            self.__last_fetched_time = time.monotonic()
            self.__last_fetched_payload = response.text
            return response.text

    def __cache_is_valid(self) -> bool:
        if self.__last_fetched_payload is None:
            return False
        if self.__last_fetched_time is None:
            return False
        if time.monotonic() - self.__last_fetched_time > self.__cache_expiry:
            return False
        return True
