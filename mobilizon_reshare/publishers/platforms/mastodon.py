from typing import Optional
from urllib.parse import urljoin

import pkg_resources
import requests
from requests import Response

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.publishers.exceptions import (
    InvalidBot,
    InvalidEvent,
    InvalidResponse,
    HTTPResponseError,
    InvalidMessage,
)


class MastodonFormatter(AbstractEventFormatter):

    _conf = ("publisher", "mastodon")
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "mastodon.tmpl.j2"
    )

    default_recap_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "mastodon_recap.tmpl.j2"
    )

    default_recap_header_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "mastodon_recap_header.tmpl.j2"
    )

    def _validate_event(self, event: MobilizonEvent) -> None:
        text = event.description
        if not (text and text.strip()):
            self._log_error("No text was found", raise_error=InvalidEvent)

    def _validate_message(self, message) -> None:
        if len(message.encode("utf-8")) >= self.conf.toot_length:
            self._log_error("Message is too long", raise_error=InvalidMessage)


class MastodonPlatform(AbstractPlatform):
    """
    Mastodon publisher class.
    """

    _conf = ("publisher", "mastodon")
    api_uri = "api/v1/"
    name = "mastodon"

    def _send(self, message: str, event: Optional[MobilizonEvent] = None) -> Response:
        """
        Send messages
        """
        return requests.post(
            url=urljoin(self.conf.instance, self.api_uri) + "statuses",
            headers={"Authorization": f"Bearer {self.conf.token}"},
            data={"status": message, "visibility": "public"},
        )

    def validate_credentials(self):
        res = requests.get(
            headers={"Authorization": f"Bearer {self.conf.token}"},
            url=urljoin(self.conf.instance, self.api_uri) + "apps/verify_credentials",
        )
        data = self._validate_response(res)

        if not self.conf.name == data["name"]:
            self._log_error(
                "Found a different bot than the expected one"
                f"\n\tfound: {data['name']}"
                f"\n\texpected: {self.conf.name}",
                raise_error=InvalidBot,
            )

    def _validate_response(self, res: Response) -> dict:
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self._log_debug(str(res))
            self._log_error(
                str(e), raise_error=HTTPResponseError,
            )

        try:
            data = res.json()
        except Exception as e:
            self._log_error(
                f"Server returned invalid json data: {str(e)}",
                raise_error=InvalidResponse,
            )

        return data


class MastodonPublisher(MastodonPlatform):

    _conf = ("publisher", "mastodon")


class MastodonNotifier(MastodonPlatform):

    _conf = ("notifier", "mastodon")
