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
    InvalidCredentials,
    InvalidEvent,
    InvalidResponse,
    PublisherError,
    ServerError,
    ClientError,
)
from mobilizon_reshare.publishers.platforms.utils import uri_join, fqdn_to_uri


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

    def validate_event(self, event: MobilizonEvent) -> None:
        text = event.description
        if not (text and text.strip()):
            self._log_error("No text was found", raise_error=InvalidEvent)

    def validate_message(self, message) -> None:
        if len(message.encode("utf-8")) >= 500:
            raise PublisherError("Message is too long")


class MastodonPlatform(AbstractPlatform):
    """
    Mastodon publisher class.
    """

    _conf = ("publisher", "mastodon")
    api_uri = "api/v1/"

    def _send(self, message: str) -> Response:
        """
        Send messages
        """
        return requests.post(
            url=uri_join(fqdn_to_uri(self.conf.instance), self.api_uri) + "statuses",
            headers={"Authorization": f"Bearer {self.conf.token}"},
            data={
                "status": message,
                "visibility": "public",
            },
        )

    def validate_credentials(self):
        conf = self.conf
        instance = conf.instance
        token = conf.token
        name = conf.name
        err = []
        if not name:
            err.append("application name")
        if not instance:
            err.append("instance domain name")
        if not token:
            err.append("application token")
        if err:
            self._log_error(
                ", ".join(err) + " is/are missing",
                raise_error=InvalidCredentials,
            )

        res = requests.get(
            headers={"Authorization": f"Bearer {token}"},
            url=uri_join(fqdn_to_uri(instance), self.api_uri)
            + "apps/verify_credentials",
        )
        data = self._validate_response(res)

        if not name == data["name"]:
            self._log_error(
                "Found a different bot than the expected one"
                f"\n\tfound: {data['name']}"
                f"\n\texpected: {name}",
                raise_error=InvalidBot,
            )

    def _validate_response(self, res: Response) -> dict:
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            self._log_debug(str(res))
            self._log_error(
                f"{res.status_code} ERROR",
                raise_error=ServerError if res.status_code >= 500 else ClientError,
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
