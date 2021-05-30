from tortoise import fields
from tortoise.models import Model

from mobilizon_bots.event.event import NotificationStatus


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
