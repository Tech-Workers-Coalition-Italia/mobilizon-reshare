from enum import IntEnum

from tortoise import fields
from tortoise.models import Model


class PublicationStatus(IntEnum):
    WAITING = 1
    FAILED = 2
    COMPLETED = 3


class Publication(Model):
    id = fields.UUIDField(pk=True)
    status = fields.IntEnumField(PublicationStatus)

    # When a Publication's status is WAITING
    # we don't need a timestamp nor a reason
    timestamp = fields.DatetimeField(null=True)
    reason = fields.TextField(null=True)

    event = fields.ForeignKeyField("models.Event", related_name="publications")
    publisher = fields.ForeignKeyField("models.Publisher", related_name="publications")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        table = "publication"
