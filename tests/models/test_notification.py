import pytest

from mobilizon_bots.event.event import NotificationStatus
from mobilizon_bots.models.notification import Notification


@pytest.mark.asyncio
async def test_notification_create(notification_model_generator):
    notification_model = notification_model_generator()
    await notification_model.save()
    notification_db = await Notification.all().first()
    assert notification_db.status == NotificationStatus.WAITING
    assert notification_db.message == "message1"
