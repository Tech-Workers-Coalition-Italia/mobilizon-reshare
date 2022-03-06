from typing import Optional
from urllib.parse import urljoin

import pkg_resources
import requests
from requests import Response
from requests.auth import HTTPBasicAuth

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.formatting.description import html_to_markdown
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.publishers.exceptions import (
    InvalidBot,
    InvalidEvent,
    InvalidResponse,
    ZulipError,
    InvalidMessage,
    HTTPResponseError,
)


class ZulipFormatter(AbstractEventFormatter):

    _conf = ("publisher", "zulip")
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "zulip.tmpl.j2"
    )

    default_recap_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "zulip_recap.tmpl.j2"
    )

    default_recap_header_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "zulip_recap_header.tmpl.j2"
    )

    def _validate_event(self, event: MobilizonEvent) -> None:
        text = event.description
        if not (text and text.strip()):
            self._log_error("No text was found", raise_error=InvalidEvent)

    def _validate_message(self, message: str) -> None:
        if len(message.encode("utf-8")) >= 10000:
            self._log_error("Message is too long", raise_error=InvalidMessage)

    def _preprocess_event(self, event: MobilizonEvent):
        event.description = html_to_markdown(event.description)
        event.name = html_to_markdown(event.name)
        return event


class ZulipPlatform(AbstractPlatform):
    """
    Zulip publisher class.
    """

    _conf = ("publisher", "zulip")
    api_uri = "api/v1/"
    name = "zulip"

    def _send(self, message: str, event: Optional[MobilizonEvent] = None) -> Response:
        """
        Send stream messages
        """
        return requests.post(
            url=urljoin(self.conf.instance, self.api_uri) + "messages",
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

        res = requests.get(
            auth=HTTPBasicAuth(self.conf.bot_email, self.conf.bot_token),
            url=urljoin(self.conf.instance, self.api_uri) + "users/me",
        )
        data = self._validate_response(res)

        if not data["is_bot"]:
            self._log_error(
                "These user is not a bot", raise_error=InvalidBot,
            )

        if not conf.bot_email == data["email"]:
            self._log_error(
                "Found a different bot than the expected one"
                f"\n\tfound: {data['email']}"
                f"\n\texpected: {conf.bot_email}",
                raise_error=InvalidBot,
            )

    def _validate_response(self, response: Response) -> dict:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self._log_debug(str(response))
            self._log_error(
                str(e), raise_error=HTTPResponseError,
            )

        # See https://zulip.com/api/rest-error-handling
        try:
            data = response.json()
        except Exception as e:
            self._log_error(
                f"Server returned invalid json data: {str(e)}",
                raise_error=InvalidResponse,
            )

        if data["result"] == "error":
            self._log_error(
                f"{response.status_code} Error - {data['msg']}", raise_error=ZulipError,
            )

        return data


class ZulipPublisher(ZulipPlatform):

    _conf = ("publisher", "zulip")


class ZulipNotifier(ZulipPlatform):

    _conf = ("notifier", "zulip")
