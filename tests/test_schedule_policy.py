#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from banana.primitives.policy.SchedulePolicy import SchedulePolicy


def test_formats_item_when_predicate_allows_notification():
    policy = SchedulePolicy(
        formatter=lambda item: f"formatted {item}",
        predicate=lambda item: item == "allowed",
    )

    assert asyncio.run(policy.evaluate("allowed")) == "formatted allowed"


def test_returns_none_when_predicate_suppresses_notification():
    policy = SchedulePolicy(
        formatter=lambda item: f"formatted {item}",
        predicate=lambda _: False,
    )

    assert asyncio.run(policy.evaluate("suppressed")) is None
