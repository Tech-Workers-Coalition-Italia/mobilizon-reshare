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
            self._log_error_and_raise(
                InvalidCredentials, ", ".join(err) + " is/are missing"
            )

        res = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        data = self._validate_response(res)

        if not username == data.get("result", {}).get("username"):
            self._log_error_and_raise(
                InvalidBot, "Found a different bot than the expected one"
            )

    def validate_event(self) -> None:
        text = self.event.description
        if not (text and text.strip()):
            self._log_error_and_raise(InvalidEvent, "No text was found")

    def _validate_response(self, res):
        res.raise_for_status()

        try:
            data = res.json()
        except Exception as e:
            self._log_error_and_raise(
                InvalidResponse, f"Server returned invalid json data: {str(e)}"
            )

        if not data.get("ok"):
            self._log_error_and_raise(
                InvalidResponse, f"Invalid request (response: {data})"
            )

        return data

    def validate_message(self) -> None:
        # TODO implement
        pass
