import requests

from mobilizon_bots.config.config import settings

from .abstract import AbstractPublisher
from .exceptions import (
    InvalidBot,
    InvalidCredentials,
    InvalidEvent,
    InvalidResponse,
    InvalidSettings,
)


class TelegramPublisher(AbstractPublisher):
    def post(self):
        attrs = self.get_attrs_from_conf()
        res = requests.post(
            url=f"https://api.telegram.org/bot{attrs['token']}/sendMessage",
            params={"chat_id": attrs["chat_id"], "text": self.message},
        )
        try:
            self._validate_response(res)
            return True
        except InvalidResponse:
            return False

    def validate_credentials(self):
        attrs = self.get_attrs_from_conf()
        chat_id = attrs.get("chat_id")
        token = attrs.get("token")
        username = attrs.get("username")
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

    def get_attrs_from_conf(self, log=None):
        if log is None:
            log = self._log_error
        try:
            conf = settings.PUBLISHER.telegram
        except AttributeError:
            conf = None
            log(InvalidSettings, "Could not retrieve Telegram settings")
        try:
            chat_id = conf.chat_id
        except AttributeError:
            chat_id = ""
            log(InvalidSettings, "Could not retrieve Telegram Chat ID")
        try:
            token = conf.token
        except AttributeError:
            token = ""
            log(InvalidSettings, "Could not retrieve Telegram Token")
        try:
            username = conf.username
        except AttributeError:
            username = ""
            log(InvalidSettings, "Could not retrieve Telegram Username")
        return {
            "conf": conf,
            "chat_id": chat_id,
            "token": token,
            "username": username,
        }

    def get_message_from_event(self) -> str:
        # TODO implement
        return self.event.description

    def validate_message(self):
        # TODO implement
        pass
