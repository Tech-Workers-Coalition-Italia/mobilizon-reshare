from tortoise import fields
from tortoise.models import Model

from mobilizon_reshare.models.publication import PublicationStatus, Publication
from mobilizon_reshare.models.publisher import Publisher
from mobilizon_reshare.publishers import get_active_publishers


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

    async def build_unsaved_publication_models(self):
        result = []
        publishers = get_active_publishers()
        for publisher in publishers:
            result.append(
                await self.build_publication_by_publisher_name(
                    publisher, PublicationStatus.UNSAVED
                )
            )
        return result

    async def build_publication_by_publisher_name(
        self, publisher_name: str, status: PublicationStatus
    ) -> Publication:
        publisher = await Publisher.filter(name=publisher_name).first()
        return Publication(
            status=status,
            event_id=self.id,
            publisher_id=publisher.id,
            publisher=publisher,
        )
