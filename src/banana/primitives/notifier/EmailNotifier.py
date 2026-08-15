#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ("EmailNotifier",)

import logging
import smtplib
from email.message import EmailMessage

from .NotifierPrimitives import NotifierPrimitives


logger = logging.getLogger(__name__)


class EmailNotifier(NotifierPrimitives[str]):
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

    async def notify(self, item: str) -> None:
        message = EmailMessage()

        message["From"] = self.__sender
        message["To"] = self.__sender
        message["Bcc"] = ", ".join(self.__recipients)
        message["Subject"] = self.__subject
        
        message.set_content(item)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.__sender, self.__password)
            smtp.send_message(message)

        logger.info(
            "Sent schedule notification '%s' to %s recipient(s)",
            self.__subject,
            len(self.__recipients),
        )
