from typing import Optional

import facebook
import pkg_resources
from facebook import GraphAPIError

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.formatting.description import html_to_plaintext
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.publishers.exceptions import (
    InvalidCredentials,
    InvalidEvent,
    InvalidMessage,
    PublisherError,
)


class FacebookFormatter(AbstractEventFormatter):

    _conf = ("publisher", "facebook")
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "facebook.tmpl.j2"
    )

    default_recap_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "facebook_recap.tmpl.j2"
    )

    default_recap_header_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "facebook_recap_header.tmpl.j2"
    )

    def _validate_event(self, event: MobilizonEvent) -> None:
        text = event.description
        if not (text and text.strip()):
            self._log_error("No text was found", raise_error=InvalidEvent)

    def _validate_message(self, message) -> None:
        if len(message) >= 63200:
            self._log_error("Message is too long", raise_error=InvalidMessage)

    def _preprocess_event(self, event: MobilizonEvent):
        event.description = html_to_plaintext(event.description)
        event.name = html_to_plaintext(event.name)
        return event


class FacebookPlatform(AbstractPlatform):
    """
    Facebook publisher class.
    """

    name = "facebook"

    def _get_api(self) -> facebook.GraphAPI:
        return facebook.GraphAPI(access_token=self.conf["page_access_token"])

    def _send(self, message: str, event: Optional[MobilizonEvent] = None):
        try:
            self._get_api().put_object(
                parent_object="me",
                connection_name="feed",
                message=message,
                link=event.mobilizon_link if event else None,
            )
        except GraphAPIError:
            self._log_error(
                "Facebook send failed", raise_error=PublisherError,
            )

    def validate_credentials(self):

        try:
            self._log_debug("Validating Facebook credentials")
            self._get_api().get_object(id="me", field="name")
        except GraphAPIError:
            self._log_error(
                "Invalid Facebook credentials. Authentication Failed",
                raise_error=InvalidCredentials,
            )

        self._log_debug("Facebook credentials are valid")

    def _validate_response(self, response):
        pass


class FacebookPublisher(FacebookPlatform):

    _conf = ("publisher", "facebook")


class FacebookNotifier(FacebookPlatform):

    _conf = ("notifier", "facebook")
