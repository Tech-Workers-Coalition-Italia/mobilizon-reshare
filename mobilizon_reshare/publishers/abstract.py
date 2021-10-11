import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from uuid import UUID

from dynaconf.utils.boxing import DynaBox
from jinja2 import Environment, FileSystemLoader, Template

from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.event.event import MobilizonEvent
from mobilizon_reshare.models.publication import Publication as PublicationModel
from .exceptions import PublisherError, InvalidAttribute

JINJA_ENV = Environment(loader=FileSystemLoader("/"))

logger = logging.getLogger(__name__)


class LoggerMixin:
    def _log_debug(self, msg, *args, **kwargs):
        self.__log(logging.DEBUG, msg, *args, **kwargs)

    def _log_info(self, msg, *args, **kwargs):
        self.__log(logging.INFO, msg, *args, **kwargs)

    def _log_warning(self, msg, *args, **kwargs):
        self.__log(logging.WARNING, msg, *args, **kwargs)

    def _log_error(self, msg, *args, **kwargs):
        self.__log(logging.ERROR, msg, *args, **kwargs)

    def _log_critical(self, msg, *args, **kwargs):
        self.__log(logging.CRITICAL, msg, *args, **kwargs)

    def __log(self, level, msg, raise_error: PublisherError = None, *args, **kwargs):
        method = inspect.currentframe().f_back.f_back.f_code.co_name
        logger.log(level, f"{self}.{method}(): {msg}", *args, **kwargs)
        if raise_error is not None:
            raise raise_error(msg)


class ConfLoaderMixin:
    _conf = tuple()

    @property
    def conf(self) -> DynaBox:
        """
        Retrieves class's settings.
        """
        cls = type(self)

        try:
            t, n = cls._conf or tuple()
            return get_settings()[t][n]
        except (KeyError, ValueError):
            raise InvalidAttribute(
                f"Class {cls.__name__} has invalid ``_conf`` attribute"
                f" (should be 2-tuple)"
            )


class AbstractPlatform(ABC, LoggerMixin, ConfLoaderMixin):
    """
    Generic notifier class.
    Shall be inherited from specific subclasses that will manage validation
    process for messages and credentials, text formatting, posting, etc.

    Attributes:
        - ``message``: a formatted ``str``
    """

    # Non-abstract subclasses should define ``_conf`` as a 2-tuple, where the
    # first element is the type of class (either 'notifier' or 'publisher') and
    # the second the name of its service (ie: 'facebook', 'telegram')

    def __repr__(self):
        return type(self).__name__

    __str__ = __repr__

    @abstractmethod
    def _send(self, message: str):
        raise NotImplementedError  # pragma: no cover

    def send(self, message: str):
        """
        Sends a message to the target channel
        """
        message = self._preprocess_message(message)
        response = self._send(message)
        self._validate_response(response)

    def _preprocess_message(self, message: str):
        return message

    @abstractmethod
    def _validate_response(self, response):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def validate_credentials(self) -> None:
        """
        Validates credentials.
        Should raise ``PublisherError`` (or one of its subclasses) if
        credentials are not valid.
        """
        raise NotImplementedError  # pragma: no cover


class AbstractEventFormatter(LoggerMixin, ConfLoaderMixin):
    @abstractmethod
    def validate_event(self, message) -> None:
        """
        Validates publisher's event.
        Should raise ``PublisherError`` (or one of its subclasses) if event
        is not valid.
        """
        raise NotImplementedError  # pragma: no cover

    def _preprocess_event(self, event):
        """
        Allows publishers to preprocess events before feeding them to the template
        """
        return event

    def get_message_from_event(self, event: MobilizonEvent) -> str:
        """
        Retrieves a message from the event itself.
        """
        event = self._preprocess_event(event)
        return event.format(self.get_message_template())

    def get_message_template(self) -> Template:
        """
        Retrieves publisher's message template.
        """
        template_path = self.conf.msg_template_path or self.default_template_path
        return JINJA_ENV.get_template(template_path)

    @abstractmethod
    def validate_message(self, message: str) -> None:
        """
        Validates notifier's message.
        Should raise ``PublisherError`` (or one of its subclasses) if message
        is not valid.
        """
        raise NotImplementedError  # pragma: no cover

    def get_recap_fragment_template(self) -> Template:
        template_path = (
            self.conf.recap_template_path or self.default_recap_template_path
        )
        return JINJA_ENV.get_template(template_path)

    def get_recap_fragment(self, event: MobilizonEvent) -> str:
        """
        Retrieves the fragment that describes a single event inside the event recap.
        """
        event = self._preprocess_event(event)
        return event.format(self.get_recap_fragment_template())


@dataclass
class BasePublication:
    publisher: AbstractPlatform
    formatter: AbstractEventFormatter


@dataclass
class EventPublication(BasePublication):
    event: MobilizonEvent
    id: UUID

    @classmethod
    def from_orm(cls, model: PublicationModel, event: MobilizonEvent):
        # imported here to avoid circular dependencies
        from mobilizon_reshare.publishers.platforms.platform_mapping import (
            get_publisher_class,
            get_formatter_class,
        )

        publisher = get_publisher_class(model.publisher.name)()
        formatter = get_formatter_class(model.publisher.name)()
        return cls(publisher, formatter, event, model.id,)


@dataclass
class RecapPublication(BasePublication):
    events: List[MobilizonEvent]
