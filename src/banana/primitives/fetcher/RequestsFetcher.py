#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("RequestsFetcher",)

from typing import Any

import requests

from .FetcherPrimitives import FetcherPrimitives


class RequestsFetcher(FetcherPrimitives[str]):
    def __init__(self, url: str, payload: dict[str, Any], timeout: int = 15):
        self.__url = url
        self.__payload = payload
        self.__timeout = timeout

    async def fetch(self) -> str:
        response = requests.post(
            self.__url,
            data=self.__payload,
            timeout=self.__timeout,
        )
        return response.text
