import pkg_resources
import requests

from .abstract import AbstractPublisher
from .exceptions import (
    InvalidBot,
    InvalidCredentials,
    InvalidEvent,
    InvalidResponse,
)


class TelegramPublisher(AbstractPublisher):
    """
    Telegram publisher class.
    """

    _conf = ("publisher", "telegram")
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_bots.publishers.templates", "telegram.tmpl.j2"
    )

    def post(self) -> None:
        conf = self.conf
        res = requests.post(
            url=f"https://api.telegram.org/bot{conf.token}/sendMessage",
            params={"chat_id": conf.chat_id, "text": self.message},
        )
        self._validate_response(res)

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

    def validate_event(self) -> None:
        text = self.event.description
        if not (text and text.strip()):
            self._log_error("No text was found", raise_error=InvalidEvent)

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

    def validate_message(self) -> None:
        # TODO implement
        pass
