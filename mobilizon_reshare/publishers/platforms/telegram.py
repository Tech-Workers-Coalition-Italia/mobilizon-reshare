import re
from typing import Optional

import pkg_resources
import requests
from requests import Response

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.formatting.description import html_to_markdown
from mobilizon_reshare.publishers.abstract import (
    AbstractEventFormatter,
    AbstractPlatform,
)
from mobilizon_reshare.publishers.exceptions import (
    InvalidBot,
    InvalidEvent,
    InvalidResponse,
    InvalidMessage,
)


class TelegramFormatter(AbstractEventFormatter):
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "telegram.tmpl.j2"
    )

    default_recap_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "telegram_recap.tmpl.j2"
    )

    default_recap_header_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "telegram_recap_header.tmpl.j2"
    )

    _conf = ("publisher", "telegram")
    _escape_characters = [
        "-",
        ".",
        "(",
        "!",
        ")",
        ">",
        "<",
        ">",
        "{",
        "}",
    ]

    @staticmethod
    def restore_links(message: str) -> str:
        """The escape_message function should ignore actually valid links that involve square brackets and parenthesis.
        This function de-escapes actual links without altering other escaped square brackets and parenthesis"""

        def build_link(match):
            result = match.group(0)
            for character in TelegramFormatter._escape_characters:
                result = result.replace("\\" + character, character)
            return result

        return re.sub(r"\[(\w*)]\\\(([\w\-/\\.:]*)\\\)", build_link, message,)

    @staticmethod
    def escape_message(message: str) -> str:
        """Escape message to comply with Telegram standards"""
        for character in TelegramFormatter._escape_characters:
            message = message.replace(character, "\\" + character)

        # Telegram doesn't use headers so # can be removed
        message = message.replace("#", r"")

        return TelegramFormatter.restore_links(message)

    def _validate_event(self, event: MobilizonEvent) -> None:
        description = event.description
        if not (description and description.strip()):
            self._log_error("No description was found", raise_error=InvalidEvent)

    def _validate_message(self, message: str) -> None:
        if len(message) >= 4096:
            self._log_error("Message is too long", raise_error=InvalidMessage)

    def _preprocess_event(self, event: MobilizonEvent):
        event.description = html_to_markdown(event.description)
        event.name = html_to_markdown(event.name)
        return event


class TelegramPlatform(AbstractPlatform):
    """
    Telegram publisher class.
    """

    name = "telegram"

    def _preprocess_message(self, message: str):
        return TelegramFormatter.escape_message(message)

    def validate_credentials(self):
        res = requests.get(f"https://api.telegram.org/bot{self.conf.token}/getMe")
        data = self._validate_response(res)

        if not self.conf.username == data.get("result", {}).get("username"):
            self._log_error(
                "Found a different bot than the expected one", raise_error=InvalidBot,
            )

    def _send(self, message: str, event: Optional[MobilizonEvent] = None) -> Response:
        return requests.post(
            url=f"https://api.telegram.org/bot{self.conf.token}/sendMessage",
            json={
                "chat_id": self.conf.chat_id,
                "text": message,
                "parse_mode": "markdownv2",
            },
        )

    def _validate_response(self, res):
        try:

            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self._log_error(
                f"Server returned invalid data: {str(e)}\n{res.text}",
                raise_error=InvalidResponse,
            )

        try:
            data = res.json()
        except Exception as e:
            self._log_error(
                f"Server returned invalid json data: {str(e)}",
                raise_error=InvalidResponse,
            )

        if not data.get("ok"):
            self._log_error(
                f"Invalid request (response: {data})", raise_error=InvalidResponse,
            )

        return data


class TelegramPublisher(TelegramPlatform):

    _conf = ("publisher", "telegram")


class TelegramNotifier(TelegramPlatform):

    _conf = ("notifier", "telegram")
