from tortoise import fields
from tortoise.models import Model


class Notification(Model):
    id = fields.UUIDField(pk=True)
    # TODO: Make actual IntEnumField
    status = fields.IntField()
    error_code = fields.IntField()

    target = fields.TextField()
    message = fields.TextField()

    publication = fields.OneToOneField(
        "models.Publication", related_name="publications", on_delete="SET_NULL"
    )

    def __str__(self):
        return self.name

    class Meta:
        table = "notification"
