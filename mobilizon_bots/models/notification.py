from tortoise import fields
from tortoise.models import Model


class Notification(Model):
    id = fields.UUIDField(pk=True)
    # TODO: Make actual IntEnumField
    status = fields.IntField()
    error_code = fields.IntField()

    target = fields.TextField()
    message = fields.TextField()

    publication = fields.ForeignKeyField(
        "models.Publication", related_name="notifications", null=True
    )

    def __str__(self):
        return f"[{self.status}] {self.message}"

    class Meta:
        table = "notification"
