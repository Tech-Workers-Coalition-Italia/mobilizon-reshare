from tortoise import fields
from tortoise.models import Model

from mobilizon_bots.event.event import PublicationStatus


class Publication(Model):
    id = fields.UUIDField(pk=True)
    status = fields.IntEnumField(PublicationStatus)

    timestamp = fields.DatetimeField()

    event = fields.ForeignKeyField("models.Event", related_name="publications")
    publisher = fields.ForeignKeyField("models.Publisher", related_name="publications")

    def __str__(self):
        return self.name

    class Meta:
        table = "publication"
