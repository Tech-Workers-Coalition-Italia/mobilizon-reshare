import inspect
import logging
from abc import ABC, abstractmethod

from dynaconf.utils.boxing import DynaBox
from jinja2 import Environment, FileSystemLoader, Template
from requests import Response

from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.event.event import MobilizonEvent
from .exceptions import PublisherError, InvalidAttribute

JINJA_ENV = Environment(loader=FileSystemLoader("/"))

logger = logging.getLogger(__name__)


class AbstractNotifier(ABC):
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
    _conf = tuple()

    def __repr__(self):
        return type(self).__name__

    __str__ = __repr__

    @property
    def conf(self) -> DynaBox:
        """
        Retrieves class's settings.
        """
        cls = type(self)
        if cls in (AbstractPublisher, AbstractNotifier):
            raise InvalidAttribute(
                "Abstract classes cannot access notifiers/publishers' settings"
            )
        try:
            t, n = cls._conf or tuple()
            return get_settings()[t][n]
        except (KeyError, ValueError):
            raise InvalidAttribute(
                f"Class {cls.__name__} has invalid ``_conf`` attribute"
                f" (should be 2-tuple)"
            )

    @abstractmethod
    def send(self, message):
        """
        Sends a message to the target channel
        """
        raise NotImplementedError

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

    def are_credentials_valid(self) -> bool:
        try:
            self.validate_credentials()
        except PublisherError:
            return False
        return True

    @abstractmethod
    def validate_credentials(self) -> None:
        """
        Validates credentials.
        Should raise ``PublisherError`` (or one of its subclasses) if
        credentials are not valid.
        """
        raise NotImplementedError

    @abstractmethod
    def publish(self) -> None:
        """
        Publishes the actual post on social media.
        Should raise ``PublisherError`` (or one of its subclasses) if
        anything goes wrong.
        """
        raise NotImplementedError

    def is_message_valid(self) -> bool:
        try:
            self.validate_message()
        except PublisherError:
            return False
        return True

    @abstractmethod
    def validate_message(self) -> None:
        """
        Validates notifier's message.
        Should raise ``PublisherError`` (or one of its subclasses) if message
        is not valid.
        """
        raise NotImplementedError


class AbstractPublisher(AbstractNotifier):
    """
    Generic publisher class.
    Shall be inherited from specific subclasses that will manage validation
    process for events and credentials, text formatting, posting, etc.

    Attributes:
        - ``event``: a ``MobilizonEvent`` containing every useful info from
            the event
        - ``message``: a formatted ``str``
    """

    _conf = tuple()

    def __init__(self, event: MobilizonEvent):
        self.event = event
        super().__init__()

    def is_event_valid(self) -> bool:
        try:
            self.validate_event()
        except PublisherError:
            return False
        return True

    @abstractmethod
    def validate_event(self) -> None:
        """
        Validates publisher's event.
        Should raise ``PublisherError`` (or one of its subclasses) if event
        is not valid.
        """
        raise NotImplementedError

    def _preprocess_event(self):
        """
        Allows publishers to preprocess events before feeding them to the template
        """
        pass

    def get_message_from_event(self) -> str:
        """
        Retrieves a message from the event itself.
        """
        self._preprocess_event()
        return self.event.format(self.get_message_template())

    def get_message_template(self) -> Template:
        """
        Retrieves publisher's message template.
        """
        template_path = self.conf.msg_template_path or self.default_template_path
        return JINJA_ENV.get_template(template_path)

    @abstractmethod
    def _send(self, message) -> Response:
        pass

    @abstractmethod
    def _validate_response(self, response: Response) -> None:
        pass

    def send(self, message):
        res = self._send(message)
        self._validate_response(res)

    def publish(self) -> None:
        self.send(message=self.get_message_from_event())
