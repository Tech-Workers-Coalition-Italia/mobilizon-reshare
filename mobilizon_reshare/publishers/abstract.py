import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from dynaconf.utils.boxing import DynaBox
from jinja2 import Environment, FileSystemLoader, Template

from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.event.event import MobilizonEvent
from .exceptions import InvalidAttribute

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

    def __log(self, level, msg, raise_error: type = None, *args, **kwargs):
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
        return self.name

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def _send(self, message: str, event: Optional[MobilizonEvent] = None):
        raise NotImplementedError  # pragma: no cover

    def send(self, message: str, event: Optional[MobilizonEvent] = None):
        """
        Sends a message to the target channel
        """
        response = self._send(message, event)
        self._validate_response(response)

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
    def _validate_event(self, event: MobilizonEvent) -> None:
        """
        Validates publisher's event.
        Should raise ``PublisherError`` (or one of its subclasses) if event
        is not valid.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _validate_message(self, message: str) -> None:
        """
        Validates notifier's message.
        Should raise ``PublisherError`` (or one of its subclasses) if message
        is not valid.
        """
        raise NotImplementedError  # pragma: no cover

    def validate_event(self, event: MobilizonEvent) -> None:
        self._validate_event(event)
        self._validate_message(self.get_message_from_event(event))

    @abstractmethod
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
        message = event.format(self.get_message_template())
        message = self._preprocess_message(message)
        return message

    def get_message_template(self) -> Template:
        """
        Retrieves publisher's message template.
        """
        template_path = self.conf.msg_template_path or self.default_template_path
        return JINJA_ENV.get_template(template_path)

    def get_recap_header(self):
        template_path = (
            self.conf.recap_header_template_path
            or self.default_recap_header_template_path
        )
        return JINJA_ENV.get_template(template_path).render()

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

    def _preprocess_message(self, message: str):
        return message


@dataclass
class BasePublication:
    publisher: AbstractPlatform
    formatter: AbstractEventFormatter


@dataclass
class EventPublication(BasePublication):
    event: MobilizonEvent
    id: UUID


@dataclass
class RecapPublication(BasePublication):
    events: List[MobilizonEvent]
