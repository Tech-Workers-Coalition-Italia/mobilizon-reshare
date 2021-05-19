from tortoise import fields
from tortoise.models import Model


class Publisher(Model):
    id = fields.UUIDField(pk=True)
    type = fields.CharField(max_length=255)
    account_ref = fields.CharField(max_length=512)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        table = "publisher"
