#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("NyUrbanScheduleEmailNotifier",)

import smtplib
from email.message import EmailMessage

from banana.models import Schedule

from .NotifierPrimitives import NotifierPrimitives


class NyUrbanScheduleEmailNotifier(
    NotifierPrimitives[Schedule.DayUpdates]
):
    def __init__(
        self,
        sender: str,
        password: str,
        recipients: list[str],
        subject: str
    ):
        self.__sender = sender
        self.__password = password
        self.__recipients = recipients
        self.__subject = subject

    async def notify(self, item: Schedule.DayUpdates) -> None:
        new_dates = [
            self.__format_day(day_update)
            for day_update in item
            if day_update.new_date
        ]
        spot_changes = [
            self.__format_day(day_update)
            for day_update in item
            if not day_update.new_date
        ]

        body = "NEW DATES\n"
        body += "\n\n".join(new_dates)
        body += "\n\nSPOT CHANGES\n"
        body += "\n\n".join(spot_changes)

        message = EmailMessage()

        message["From"] = self.__sender
        message["To"] = ", ".join(self.__recipients)
        message["Subject"] = self.__subject
        message.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.__sender, self.__password)
            smtp.send_message(message)

    @staticmethod
    def __format_day(day_update: Schedule.DayUpdate) -> str:
        lines = [day_update.date] + [
            NyUrbanScheduleEmailNotifier.__format_update(update)
            for update in day_update.updates
        ]

        return "\n".join(lines)

    @staticmethod
    def __format_update(update: Schedule.Update) -> str:
        slot = update.updated_slot

        return (
            f"  Court {slot.court} @ {slot.start_time:%I:%M %p}: "
            f"{NyUrbanScheduleEmailNotifier.\
               __format_change(update.slot_change)}"
        )

    @staticmethod
    def __format_change(change: "Schedule.Update.Change") -> str:
        Change = Schedule.Update.Change

        match change.kind:
            case Change.INCREASE:
                return (
                    f"+{change.payload} spots"
                    if change.payload is not None
                    else "more spots opened up"
                )
            case Change.DECREASE:
                return (
                    f"-{change.payload} spots"
                    if change.payload is not None
                    else "fewer spots available"
                )
            case Change.NO_CHANGE:
                return "now open"
