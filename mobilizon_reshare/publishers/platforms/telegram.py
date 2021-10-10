import re

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
    PublisherError,
)


class TelegramFormatter(AbstractEventFormatter):
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "telegram.tmpl.j2"
    )

    default_recap_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "telegram_recap.tmpl.j2"
    )

    _conf = ("publisher", "telegram")

    @staticmethod
    def restore_links(message: str) -> str:
        return re.sub(r"\[(\w*)]\\\(([\w\-/\\.:]*)\\\)", r"[\g<1>](\g<2>)", message,)

    @staticmethod
    def escape_message(message: str) -> str:
        message = (
            message.replace("-", r"\-")
            .replace(".", r"\.")
            .replace("(", r"\(")
            .replace("!", r"\!")
            .replace(")", r"\)")
            .replace("#", r"")
        )

        return TelegramFormatter.restore_links(message)

    def validate_event(self, event: MobilizonEvent) -> None:
        description = event.description
        if not (description and description.strip()):
            self._log_error("No description was found", raise_error=InvalidEvent)

    def validate_message(self, message: str) -> None:
        if len(message) >= 4096:
            raise PublisherError("Message is too long")

    def _preprocess_event(self, event: MobilizonEvent):
        event.description = html_to_markdown(event.description)
        event.name = html_to_markdown(event.name)
        return event


class TelegramPlatform(AbstractPlatform):
    """
    Telegram publisher class.
    """

    def _preprocess_message(self, message: str):
        return TelegramFormatter.escape_message(message)

    def validate_credentials(self):
        res = requests.get(f"https://api.telegram.org/bot{self.conf.token}/getMe")
        data = self._validate_response(res)

        if not self.conf.username == data.get("result", {}).get("username"):
            self._log_error(
                "Found a different bot than the expected one", raise_error=InvalidBot,
            )

    def _send(self, message) -> Response:
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
                f"Server returned invalid data: {str(e)}", raise_error=InvalidResponse,
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
