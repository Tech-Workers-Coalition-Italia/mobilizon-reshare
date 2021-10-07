import pkg_resources
from tweepy import OAuthHandler, API
from tweepy.models import Status

from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
    AbstractEventFormatter,
)
from mobilizon_reshare.publishers.exceptions import (
    InvalidCredentials,
    InvalidEvent,
    PublisherError,
)


class TwitterFormatter(AbstractEventFormatter):

    _conf = ("publisher", "twitter")
    default_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "twitter.tmpl.j2"
    )

    default_recap_template_path = pkg_resources.resource_filename(
        "mobilizon_reshare.publishers.templates", "twitter_recap.tmpl.j2"
    )

    def validate_event(self, event: MobilizonEvent) -> None:
        text = event.description
        if not (text and text.strip()):
            self._log_error("No text was found", raise_error=InvalidEvent)

    def validate_message(self, message) -> None:
        if len(message.encode("utf-8")) > 140:
            raise PublisherError("Message is too long")


class TwitterPlatform(AbstractPlatform):
    """
    Twitter publisher class.
    """

    _conf = ("publisher", "twitter")

    def _get_api(self):

        api_key = self.conf.api_key
        api_key_secret = self.conf.api_key_secret
        access_token = self.conf.access_token
        access_secret = self.conf.access_secret
        auth = OAuthHandler(api_key, api_key_secret)
        auth.set_access_token(access_token, access_secret)
        return API(auth)

    def _send(self, message: str) -> Status:
        return self._get_api().update_status(message)

    def validate_credentials(self):
        conf = self.conf
        api_key = conf.api_key
        api_key_secret = conf.api_key_secret
        access_token = conf.access_token
        access_secret = conf.access_secret
        err = []
        if not api_key:
            err.append("api_key")
        if not api_key_secret:
            err.append("api_key_secret")
        if not access_token:
            err.append("access_token")
        if not access_secret:
            err.append("access_secret")

        if err:
            self._log_error(
                ", ".join(err) + " is/are missing", raise_error=InvalidCredentials,
            )

        if not self._get_api().verify_credentials():
            raise InvalidCredentials(
                "Invalid Twitter credentials. Authentication Failed"
            )

    def _validate_response(self, res: Status) -> dict:
        pass


class TwitterPublisher(TwitterPlatform):

    _conf = ("publisher", "twitter")


class TwitterNotifier(TwitterPlatform):

    _conf = ("notifier", "twitter")
