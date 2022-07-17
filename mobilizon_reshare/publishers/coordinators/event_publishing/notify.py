from abc import ABC, abstractmethod
from typing import List

from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers import get_active_notifiers
from mobilizon_reshare.publishers.abstract import AbstractPlatform
from mobilizon_reshare.publishers.coordinators import logger
from mobilizon_reshare.publishers.coordinators.event_publishing.publish import (
    EventPublicationReport,
)
from mobilizon_reshare.publishers.platforms.platform_mapping import get_notifier_class


class Sender:
    def __init__(self, message: str, platforms: List[AbstractPlatform] = None):
        self.message = message
        self.platforms = platforms

    def send_to_all(self):
        for platform in self.platforms:
            try:
                platform.send(self.message)
            except Exception as e:
                logger.critical(f"Failed to send message:\n{self.message}")
                logger.exception(e)


class AbstractNotifiersCoordinator(ABC):
    def __init__(
        self, report: EventPublicationReport, notifiers: List[AbstractPlatform] = None
    ):
        self.platforms = notifiers or [
            get_notifier_class(notifier)() for notifier in get_active_notifiers()
        ]
        self.report = report

    @abstractmethod
    def notify_failure(self):
        pass


class PublicationFailureNotifiersCoordinator(AbstractNotifiersCoordinator):
    """
    Sends a notification of a failure report to the active platforms
    """

    def notify_failure(self):
        logger.info("Sending failure notifications")
        if self.report.status == PublicationStatus.FAILED:
            Sender(self.report.get_failure_message(), self.platforms).send_to_all()


class PublicationFailureLoggerCoordinator(PublicationFailureNotifiersCoordinator):
    """
    Logs a report to console
    """

    def notify_failure(self):
        if self.report.status == PublicationStatus.FAILED:
            logger.error(self.report.get_failure_message())
