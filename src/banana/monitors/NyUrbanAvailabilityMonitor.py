#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("NyUrbanAvailabilityMonitor", "OpenPlaySession",)

from enum import Enum

from banana.models import Schedule
from banana.primitives import (
    RequestsFetcher,
    NyUrbanScheduleParser,
    SnapshotStorerPrimitives,
    ScheduleDifferencer,
    PolicyPrimitives,
    NotifierPrimitives,
    
)
from .AvailabilityMonitor import AvailabilityMonitor


_URL = "https://www.nyurban.com/wp-admin/admin-ajax.php"


class OpenPlaySession(Enum):
    BRANDEIS_SUNDAY = {
        "action": "my_open_play_contentbb",
        "buttonid": 6,
        "gametypeid": 1,
        "filterid": 18,
    }


class NyUrbanAvailabilityMonitor(
    AvailabilityMonitor[str, Schedule.Days, Schedule.DayUpdates, str]
):
    def __init__(
        self,
        snapshot_storer: SnapshotStorerPrimitives[Schedule.Days],
        policy: PolicyPrimitives[Schedule.DayUpdates, str],
        notifier: NotifierPrimitives[str],
        polling_interval_seconds: int = 60 * 60 * 12,
        url: str = _URL,
        payload: OpenPlaySession = OpenPlaySession.BRANDEIS_SUNDAY,
    ):
        super().__init__(
            fetcher=RequestsFetcher(url, payload.value),
            parser=NyUrbanScheduleParser(),
            snapshot_storer=snapshot_storer,
            differencer=ScheduleDifferencer(),
            policy=policy,
            notifier=notifier,
            polling_interval_seconds=polling_interval_seconds
        )