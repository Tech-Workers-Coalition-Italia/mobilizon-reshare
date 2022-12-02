import pytest

from mobilizon_reshare.models.notification import Notification, NotificationStatus


@pytest.mark.asyncio
async def test_notification_create(notification_model_generator):
    notification_model = notification_model_generator()
    await notification_model.save()
    notification_db = await Notification.all().first()
    assert notification_db.status == NotificationStatus.FAILED
    assert notification_db.message == "message_1"
