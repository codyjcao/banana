#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import importlib
import threading
from types import SimpleNamespace

from banana.primitives.fetcher import RequestsFetcher


requests_fetcher_module = importlib.import_module(
    "banana.primitives.fetcher.RequestsFetcher"
)


def test_fetcher_owns_payload_and_uses_cached_response(monkeypatch):
    now = [100.0]
    calls = []

    def post(url, *, data, timeout):
        calls.append((url, data.copy(), timeout))
        return SimpleNamespace(text=f"response {len(calls)}", status_code=200)

    monkeypatch.setattr(requests_fetcher_module.requests, "post", post)
    monkeypatch.setattr(requests_fetcher_module.time, "monotonic", lambda: now[0])

    payload = {"session": "sunday"}
    fetcher = RequestsFetcher(
        "https://example.com/schedule", payload, cache_expiry=10
    )
    payload["session"] = "changed outside the fetcher"

    async def run_scenario():
        assert await fetcher.fetch() == "response 1"

        now[0] = 105.0
        assert await fetcher.fetch() == "response 1"

        now[0] = 111.0
        assert await fetcher.fetch() == "response 2"

    asyncio.run(run_scenario())

    assert calls == [
        ("https://example.com/schedule", {"session": "sunday"}, 15),
        ("https://example.com/schedule", {"session": "sunday"}, 15),
    ]


def test_concurrent_fetches_share_one_http_request(monkeypatch):
    request_started = threading.Event()
    allow_response = threading.Event()
    calls = []

    def post(url, *, data, timeout):
        calls.append((url, data.copy(), timeout))
        request_started.set()
        if not allow_response.wait(timeout=1):
            raise TimeoutError("Test did not release the HTTP response")
        return SimpleNamespace(text="response", status_code=200)

    monkeypatch.setattr(requests_fetcher_module.requests, "post", post)
    fetcher = RequestsFetcher(
        "https://example.com/schedule",
        {"session": "sunday"},
    )

    async def run_scenario():
        first = asyncio.create_task(fetcher.fetch())
        assert await asyncio.to_thread(request_started.wait, 0.5)

        second = asyncio.create_task(fetcher.fetch())
        await asyncio.sleep(0)
        allow_response.set()

        return await asyncio.wait_for(
            asyncio.gather(first, second), timeout=0.5
        )

    try:
        assert asyncio.run(run_scenario()) == ["response", "response"]
    finally:
        allow_response.set()

    assert calls == [
        ("https://example.com/schedule", {"session": "sunday"}, 15)
    ]
