from tortoise import fields
from tortoise.models import Model


class Publisher(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=256)
    # TODO: What to do with this?
    account_ref = fields.TextField(null=True)

    publications: fields.ReverseRelation["Publication"]

    def __str__(self):
        return f"{self.id}"

    class Meta:
        table = "publisher"
