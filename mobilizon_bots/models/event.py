from tortoise import fields
from tortoise.models import Model


class Event(Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField()
    description = fields.TextField()

    mobilizon_id = fields.UUIDField()
    mobilizon_link = fields.CharField(max_length=512)
    thumbnail_link = fields.CharField(max_length=512)
    location = fields.CharField(max_length=255)

    begin_datetime = fields.DatetimeField()
    end_datetime = fields.DatetimeField()
    last_accessed = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        table = "event"
