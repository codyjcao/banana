#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("RequestsFetcher",)

import logging
from typing import Any

import requests

from .FetcherPrimitives import FetcherPrimitives


logger = logging.getLogger(__name__)


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
        logger.info(
            "Fetched schedule from %s with status %s",
            self.__url,
            response.status_code,
        )
        return response.text
