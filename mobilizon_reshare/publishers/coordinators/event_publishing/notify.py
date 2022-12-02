from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from mobilizon_reshare.dataclasses import PublicationNotification, EventPublication
from mobilizon_reshare.models.notification import NotificationStatus
from mobilizon_reshare.models.publication import PublicationStatus
from mobilizon_reshare.publishers import get_active_notifiers
from mobilizon_reshare.publishers.abstract import (
    AbstractPlatform,
)
from mobilizon_reshare.publishers.coordinators import (
    logger,
    BasePublicationReport,
    BaseCoordinatorReport,
)
from mobilizon_reshare.publishers.coordinators.event_publishing import (
    EventPublicationReport,
)
from mobilizon_reshare.publishers.platforms.platform_mapping import (
    get_notifier_class,
    get_formatter_class,
)


@dataclass
class PublicationNotificationReport(BasePublicationReport):
    status: NotificationStatus
    notification: PublicationNotification

    @property
    def successful(self):
        return self.status == NotificationStatus.COMPLETED

    def get_failure_message(self):
        if not self.reason:
            logger.error("Report of failure without reason.", exc_info=True)
        return (
            f"Failed with status: {self.status.name}.\n"
            f"Reason: {self.reason}\n"
            f"Publisher: {self.notification.publisher.name}\n"
            f"Publication: {self.notification.publication.id}"
        )


@dataclass
class NotifierCoordinatorReport(BaseCoordinatorReport):
    reports: Sequence[PublicationNotificationReport]
    notifications: Sequence[PublicationNotification] = field(default_factory=list)


class Sender:
    def __init__(
        self,
        message: str,
        publication: EventPublication,
        platforms: List[AbstractPlatform] = None,
    ):
        self.message = message
        self.platforms = platforms
        self.publication = publication

    def send_to_all(self) -> NotifierCoordinatorReport:
        reports = []
        notifications = []
        for platform in self.platforms:
            notification = PublicationNotification(
                platform, get_formatter_class(platform.name)(), self.publication
            )
            try:
                platform.send(self.message)
                report = PublicationNotificationReport(
                    NotificationStatus.COMPLETED, self.message, notification
                )
            except Exception as e:
                msg = f"[{platform.name}] Failed to notify failure of message:\n{self.message}"
                logger.critical(msg)
                logger.exception(e)
                report = PublicationNotificationReport(
                    NotificationStatus.FAILED, msg, notification
                )
            notifications.append(notification)
            reports.append(report)
        return NotifierCoordinatorReport(reports=reports, notifications=notifications)


class AbstractNotifiersCoordinator(ABC):
    def __init__(
        self, report: BasePublicationReport, notifiers: List[AbstractPlatform] = None
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

    report: EventPublicationReport
    platforms: List[AbstractPlatform]

    def notify_failure(self) -> Optional[NotifierCoordinatorReport]:
        logger.info("Sending failure notifications")
        if self.report.status == PublicationStatus.FAILED:
            return Sender(
                self.report.get_failure_message(),
                self.report.publication,
                self.platforms,
            ).send_to_all()


class PublicationFailureLoggerCoordinator(PublicationFailureNotifiersCoordinator):
    """
    Logs a report to console
    """

    def notify_failure(self):
        if self.report.status == PublicationStatus.FAILED:
            logger.error(self.report.get_failure_message())
