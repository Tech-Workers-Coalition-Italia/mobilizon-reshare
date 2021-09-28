import pkg_resources
import requests
from requests import Response

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.formatting.description import html_to_markdown
from mobilizon_reshare.publishers.abstract import (
    AbstractEventFormatter,
    AbstractNotifier,
)
from mobilizon_reshare.publishers.exceptions import (
    InvalidBot,
    InvalidCredentials,
    InvalidEvent,
    InvalidResponse,
)


class TelegramFormatter(AbstractEventFormatter):
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "telegram.tmpl.j2"
    )

    _conf = ("publisher", "telegram")

    @staticmethod
    def escape_message(message: str) -> str:
        message = (
            message.replace("-", "\\-")
            .replace(".", "\\.")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("#", "")
        )
        return message

    def validate_event(self, event: MobilizonEvent) -> None:
        text = event.description
        if not (text and text.strip()):
            self._log_error("No text was found", raise_error=InvalidEvent)

    def get_message_from_event(self, event: MobilizonEvent) -> str:
        return super(TelegramFormatter, self).get_message_from_event(event)

    def validate_message(self, message: str) -> None:
        # TODO implement
        pass

    def _preprocess_event(self, event: MobilizonEvent):
        event.description = html_to_markdown(event.description)
        event.name = html_to_markdown(event.name)
        return event


class TelegramPublisher(AbstractNotifier):
    """
    Telegram publisher class.
    """

    _conf = ("publisher", "telegram")

    def _preprocess_message(self, message: str):
        return TelegramFormatter.escape_message(message)

    def validate_credentials(self):
        conf = self.conf
        chat_id = conf.chat_id
        token = conf.token
        username = conf.username
        err = []
        if not chat_id:
            err.append("chat ID")
        if not token:
            err.append("token")
        if not username:
            err.append("username")
        if err:
            self._log_error(
                ", ".join(err) + " is/are missing", raise_error=InvalidCredentials,
            )

        res = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        data = self._validate_response(res)

        if not username == data.get("result", {}).get("username"):
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
