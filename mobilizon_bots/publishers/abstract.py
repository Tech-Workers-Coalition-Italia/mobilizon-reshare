import inspect
import logging

from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AbstractPublisher(ABC):
    """
    Generic publisher class.

    Shall be inherited from specific subclasses that will manage validation
    process for events and credentials, text formatting, posting, etc.

    Class attributes:
        - ``credentials``: a ``dict`` containing every useful info that the
            current publisher will need to correctly login to its platform
        - ``event``: a ``dict`` containing every useful info from the event
    """

    # TODO: will the actual event be managed by its own class?
    def __init__(self, credentials: dict, event: dict):
        self.credentials = credentials
        self.event = event

    def __repr__(self):
        return type(self).__name__

    __str__ = __repr__

    @abstractmethod
    def post(self) -> bool:
        """
        Publishes the actual post on social media using ``data`` info.
        :return: True or False according to whether publisher was able to
            complete its task
        """
        raise NotImplementedError

    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validates credentials.
        :return: True or False according to whether credentials are valid.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_event(self) -> bool:
        """
        Validates publisher's event.
        :return: True or False according to whether event is valid.
        """
        raise NotImplementedError

    def log_debug(self, msg, *args, **kwargs):
        self.__log(logging.DEBUG, msg, *args, **kwargs)

    def log_info(self, msg, *args, **kwargs):
        self.__log(logging.INFO, msg, *args, **kwargs)

    def log_warning(self, msg, *args, **kwargs):
        self.__log(logging.WARNING, msg, *args, **kwargs)

    def log_error(self, msg, *args, **kwargs):
        self.__log(logging.ERROR, msg, *args, **kwargs)

    def log_critical(self, msg, *args, **kwargs):
        self.__log(logging.CRITICAL, msg, *args, **kwargs)

    def __log(self, level, msg, *args, **kwargs):
        method = inspect.currentframe().f_back.f_back.f_code.co_name
        logger.log(level, f"{self}.{method}(): {msg}", *args, **kwargs)
