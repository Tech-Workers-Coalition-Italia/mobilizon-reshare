import re
from typing import Optional

import pkg_resources
import requests
from bs4 import BeautifulSoup
from requests import Response

from mobilizon_reshare.event.event import MobilizonEvent
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

    def _validate_event(self, event: MobilizonEvent) -> None:
        description = event.description
        if not (description and description.strip()):
            self._log_error("No description was found", raise_error=InvalidEvent)

    def _validate_message(self, message: str) -> None:
        if (
            len("".join(BeautifulSoup(message, "html.parser").findAll(text=True)))
            >= 4096
        ):
            self._log_error("Message is too long", raise_error=InvalidMessage)

    def _preprocess_message(self, message: str) -> str:
        """
        This function converts HTML5 to Telegram's HTML dialect
        :param message: a HTML5 string
        :return: a HTML string compatible with Telegram
        """
        html = BeautifulSoup(message, "html.parser")
        # replacing paragraphs
        for tag in html.findAll(["p", "br"]):
            tag.append("\n")
            tag.replaceWithChildren()
        # replacing headers
        for tag in html.findAll(["h1", "h2", "h3"]):
            if tag.text:  # only if they are not empty
                tag.name = "b"
                tag.insert_after("\n")
                tag.insert_before("\n")
            else:
                tag.decompose()
        # removing lists
        for tag in html.findAll("ul"):
            tag.unwrap()
        # replacing list elements with dots
        for tag in html.findAll(["li"]):
            tag.insert(0, "• ")
            tag.unwrap()
        # cleaning html trailing whitespace
        for tag in html.findAll("a"):
            tag["href"] = tag["href"].replace(" ", "").strip().lstrip()
        s = str(html)
        return re.sub(r"\n{2,}", "\n\n", s).strip()  # remove multiple newlines


class TelegramPlatform(AbstractPlatform):
    """
    Telegram publisher class.
    """

    name = "telegram"

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
            json={"chat_id": self.conf.chat_id, "text": message, "parse_mode": "html"},
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
