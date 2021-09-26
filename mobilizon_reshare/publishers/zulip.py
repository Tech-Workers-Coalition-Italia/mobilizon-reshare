import pkg_resources
import requests
from requests import Response
from requests.auth import HTTPBasicAuth

from mobilizon_reshare.formatting.description import html_to_markdown
from mobilizon_reshare.publishers.abstract import AbstractPublisher
from mobilizon_reshare.publishers.exceptions import (
    InvalidBot,
    InvalidCredentials,
    InvalidEvent,
    InvalidResponse,
    ZulipError,
)


class ZulipPublisher(AbstractPublisher):
    """
    Zulip publisher class.
    """

    _conf = ("publisher", "zulip")
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "zulip.tmpl.j2"
    )
    api_uri = "https://zulip.twc-italia.org/api/v1/"

    def _send_private(self, message: str) -> Response:
        """
        Send private messages
        """
        return requests.post(
            url=self.api_uri + "messages",
            auth=HTTPBasicAuth(self.conf.bot_email, self.conf.bot_token),
            data={
                "type": "private",
                "to": f"[{self.user_id}]",
                "content": message,
            },
        )

    def _send(self, message: str) -> Response:
        """
        Send stream messages
        """
        return requests.post(
            url=self.api_uri + "messages",
            auth=HTTPBasicAuth(self.conf.bot_email, self.conf.bot_token),
            data={
                "type": "stream",
                "to": self.conf.chat_id,
                "subject": self.conf.subject,
                "content": message,
            },
        )

    def validate_credentials(self):
        conf = self.conf
        chat_id = conf.chat_id
        bot_token = conf.bot_token
        bot_email = conf.bot_email
        err = []
        if not chat_id:
            err.append("chat ID")
        if not bot_token:
            err.append("bot token")
        if not bot_email:
            err.append("bot email")
        if err:
            self._log_error(
                ", ".join(err) + " is/are missing",
                raise_error=InvalidCredentials,
            )

        res = requests.get(
            auth=HTTPBasicAuth(self.conf.bot_email, self.conf.bot_token),
            url=self.api_uri + "users/me",
        )
        data = self._validate_response(res)

        if not data["is_bot"]:
            self._log_error(
                "These user is not a bot",
                raise_error=InvalidBot,
            )

        if not bot_email == data["email"]:
            self._log_error(
                "Found a different bot than the expected one"
                f"\n\tfound: {data['email']}"
                f"\n\texpected: {bot_email}",
                raise_error=InvalidBot,
            )

    def validate_event(self) -> None:
        text = self.event.description
        if not (text and text.strip()):
            self._log_error("No text was found", raise_error=InvalidEvent)

    def validate_message(self) -> None:
        # We don't need this for Zulip.
        pass

    def _validate_response(self, res) -> dict:
        # See https://zulip.com/api/rest-error-handling
        try:
            data = res.json()
        except Exception as e:
            self._log_error(
                f"Server returned invalid json data: {str(e)}",
                raise_error=InvalidResponse,
            )

        if data["result"] == "error":
            self._log_error(
                f"{res.status_code} Error - {data['msg']}",
                raise_error=ZulipError,
            )

        return data

    def _preprocess_event(self):
        self.event.description = html_to_markdown(self.event.description)
        self.event.name = html_to_markdown(self.event.name)
