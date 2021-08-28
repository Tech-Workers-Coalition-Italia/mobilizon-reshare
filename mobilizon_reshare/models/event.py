from tortoise import fields
from tortoise.models import Model


class Event(Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField()
    description = fields.TextField(null=True)

    mobilizon_id = fields.UUIDField()
    mobilizon_link = fields.TextField()
    thumbnail_link = fields.TextField(null=True)

    location = fields.TextField(null=True)

    begin_datetime = fields.DatetimeField()
    end_datetime = fields.DatetimeField()

    publications: fields.ReverseRelation["Publication"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        table = "event"
