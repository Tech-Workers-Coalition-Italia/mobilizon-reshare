import inspect
import logging

from abc import ABC, abstractmethod

from mobilizon_bots.event.event import MobilizonEvent
from .exceptions import PublisherError

logger = logging.getLogger(__name__)


class AbstractMessenger(ABC):
    def __init__(self, message: str):
        self.message = message

    def __repr__(self):
        return type(self).__name__

    __str__ = __repr__

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

    def __log(self, level, msg, *args, **kwargs):
        method = inspect.currentframe().f_back.f_back.f_code.co_name
        logger.log(level, f"{self}.{method}(): {msg}", *args, **kwargs)

    def _log_error_and_raise(self, error_class, message):
        self._log_error(message)
        raise error_class(message)

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
    def post(self) -> None:
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
        Validates messenger's message.
        Should raise ``PublisherError`` (or one of its subclasses) if message
        is not valid.
        """
        raise NotImplementedError


class AbstractPublisher(AbstractMessenger):
    """
    Generic publisher class.

    Shall be inherited from specific subclasses that will manage validation
    process for events and credentials, text formatting, posting, etc.

    Class attributes:
        - ``event``: a ``MobilizonEvent`` containing every useful info from
            the event
    """

    def __init__(self, event: MobilizonEvent):
        self.event = event
        super().__init__(message=self.get_message_from_event())

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

    @abstractmethod
    def get_message_from_event(self) -> str:
        """
        Retrieves a message from the event itself.
        """
        raise NotImplementedError
