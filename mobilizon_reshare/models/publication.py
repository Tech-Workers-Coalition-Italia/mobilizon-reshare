from enum import IntEnum

from tortoise import fields
from tortoise.models import Model

from mobilizon_reshare.models import WithPydantic


class PublicationStatus(IntEnum):
    FAILED = 0
    COMPLETED = 1


class Publication(Model, WithPydantic):
    id = fields.UUIDField(pk=True)
    status = fields.IntEnumField(PublicationStatus)

    timestamp = fields.DatetimeField()
    reason = fields.TextField(null=True)

    event = fields.ForeignKeyField("models.Event", related_name="publications")
    publisher = fields.ForeignKeyField("models.Publisher", related_name="publications")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        table = "publication"
