import hypothesis
from hypothesis import assume
from hypothesis.provisional import urls
from hypothesis.strategies import characters, datetimes, text, sampled_from

from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus


@hypothesis.strategies.composite
def events(draw, published: bool = False):
    begin_datetime = draw(datetimes())
    end_datetime = draw(datetimes())
    assume(begin_datetime < end_datetime)

    return MobilizonEvent(
        name=draw(characters()),
        description=draw(text()),
        begin_datetime=begin_datetime,
        end_datetime=end_datetime,
        last_accessed=draw(datetimes()),
        mobilizon_link=draw(urls()),
        mobilizon_id=draw(characters()),
        thumbnail_link=draw(urls()),
        location=draw(text()),
        publication_time=draw(datetimes()) if published else None,
        publication_status=draw(
            sampled_from(
                [PublicationStatus.COMPLETED, PublicationStatus.PARTIAL]
                if published
                else [PublicationStatus.WAITING, PublicationStatus.FAILED]
            )
        ),
    )
