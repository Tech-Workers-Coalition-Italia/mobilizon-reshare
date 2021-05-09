from tortoise import fields
from tortoise.models import Model


class Event(Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField()
    description = fields.TextField()

    mobilizon_id = fields.UUIDField()
    mobilizon_link = fields.TextField()
    thumbnail_link = fields.TextField()

    location = fields.TextField()

    begin_datetime = fields.DatetimeField()
    end_datetime = fields.DatetimeField()
    last_accessed = fields.DatetimeField()

    def __str__(self):
        return self.name

    class Meta:
        table = "event"
