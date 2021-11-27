from typing import Optional

import facebook
import pkg_resources

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.publishers.exceptions import (
    InvalidCredentials,
    InvalidEvent,
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
        pass


class FacebookPlatform(AbstractPlatform):
    """
    Facebook publisher class.
    """

    name = "facebook"

    def _get_api(self):
        return facebook.GraphAPI(
            access_token=self.conf["page_access_token"], version="8.0"
        )

    def _send(self, message: str, event: Optional[MobilizonEvent] = None):
        self._get_api().put_object(
            parent_object="me",
            connection_name="feed",
            message=message,
            link=event.mobilizon_link if event else None,
        )

    def validate_credentials(self):

        try:
            self._get_api().get_object(id="me", field="name")
        except Exception:
            self._log_error(
                "Invalid Facebook credentials. Authentication Failed",
                raise_error=InvalidCredentials,
            )

    def _validate_response(self, response):
        pass


class FacebookPublisher(FacebookPlatform):

    _conf = ("publisher", "facebook")


class FacebookNotifier(FacebookPlatform):

    _conf = ("notifier", "facebook")
