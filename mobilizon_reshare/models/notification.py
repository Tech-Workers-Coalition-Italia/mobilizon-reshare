from enum import IntEnum

from tortoise import fields
from tortoise.models import Model


class NotificationStatus(IntEnum):
    WAITING = 1
    FAILED = 2
    PARTIAL = 3
    COMPLETED = 4


class Notification(Model):
    id = fields.UUIDField(pk=True)
    status = fields.IntEnumField(NotificationStatus)

    message = fields.TextField()

    target = fields.ForeignKeyField(
        "models.Publisher", related_name="notifications", null=True
    )

    publication = fields.ForeignKeyField(
        "models.Publication", related_name="notifications", null=True
    )

    def __str__(self):
        return f"[{self.status}] {self.message}"

    class Meta:
        table = "notification"
