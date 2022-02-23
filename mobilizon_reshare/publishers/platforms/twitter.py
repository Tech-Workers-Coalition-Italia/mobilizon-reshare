from typing import Optional

import pkg_resources
from tweepy import OAuthHandler, API, TweepyException
from tweepy.models import Status

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.publishers.exceptions import (
    InvalidCredentials,
    PublisherError,
    InvalidMessage,
)


class TwitterFormatter(AbstractEventFormatter):

    _conf = ("publisher", "twitter")
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "twitter.tmpl.j2"
    )

    default_recap_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "twitter_recap.tmpl.j2"
    )

    default_recap_header_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "twitter_recap_header.tmpl.j2"
    )

    def _validate_event(self, event: MobilizonEvent) -> None:
        pass  # pragma: no cover

    def _validate_message(self, message) -> None:
        # TODO this is not precise. It should count the characters according to Twitter's logic but
        # Tweepy doesn't seem to support the validation client side
        if len(message.encode("utf-8")) > 280:
            self._log_error("Message is too long", raise_error=InvalidMessage)


class TwitterPlatform(AbstractPlatform):
    """
    Twitter publisher class.
    """

    _conf = ("publisher", "twitter")
    name = "twitter"

    def _get_api(self):

        api_key = self.conf.api_key
        api_key_secret = self.conf.api_key_secret
        access_token = self.conf.access_token
        access_secret = self.conf.access_secret
        auth = OAuthHandler(api_key, api_key_secret)
        auth.set_access_token(access_token, access_secret)
        return API(auth)

    def _send(self, message: str, event: Optional[MobilizonEvent] = None) -> Status:
        try:
            return self._get_api().update_status(message)
        except TweepyException as e:
            self._log_error(e.args[0], raise_error=PublisherError)

    def validate_credentials(self):
        if not self._get_api().verify_credentials():
            self._log_error(
                "Invalid Twitter credentials. Authentication Failed",
                raise_error=InvalidCredentials,
            )

    def _validate_response(self, res: Status) -> dict:
        pass  # pragma: no cover


class TwitterPublisher(TwitterPlatform):

    _conf = ("publisher", "twitter")


class TwitterNotifier(TwitterPlatform):

    _conf = ("notifier", "twitter")
