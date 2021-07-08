from http import HTTPStatus
from typing import List, Optional

import arrow
import requests

from mobilizon_bots.config.config import get_settings
from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus


class MobilizonRequestFailed(Exception):
    # TODO move to an error module
    pass


def parse_location(data):
    # TODO define a better logic (or a customizable strategy) to get the location
    return (data.get("physicalAddress", {}) or {}).get("locality") or data.get(
        "onlineAddress"
    )


def parse_picture(data):
    return (data.get("picture", {}) or {}).get("url")


def parse_event(data):
    return MobilizonEvent(
        name=data["title"],
        description=data.get("description", None),
        begin_datetime=arrow.get(data["beginsOn"]) if "beginsOn" in data else None,
        end_datetime=arrow.get(data["endsOn"]) if "endsOn" in data else None,
        mobilizon_link=data.get("url", None),
        mobilizon_id=data["uuid"],
        thumbnail_link=parse_picture(data),
        location=parse_location(data),
        publication_time=None,
        publication_status=PublicationStatus.WAITING,
    )


query_future_events = """{{
            group(preferredUsername: "{group}") {{
              organizedEvents(page:{page}, afterDatetime:"{afterDatetime}"){{
                elements {{
                  title,
                  url,
                  beginsOn,
                  endsOn,
                  options {{
                    showStartTime,
                    showEndTime,
                  }},
                  uuid,
                  description,
                  onlineAddress,
                  physicalAddress {{
                    locality,
                    description,
                    region
                  }},
                  picture {{
                    url
                    }},
                }},
              }}
            }}
          }}"""


def get_unpublished_events(published_events: List[MobilizonEvent]):
    # I take all the future events
    future_events = get_mobilizon_future_events()
    # I get the ids of all the published events coming from the DB
    published_events_id = set(map(lambda x: x.mobilizon_id, published_events))
    # I keep the future events only the ones that haven't been published
    # Note: some events might exist in the DB and be unpublished. Here they should be ignored because the information
    # in the DB might be old and the event might have been updated.
    # We assume the published_events list doesn't contain such events.
    return list(
        filter(lambda x: x.mobilizon_id not in published_events_id, future_events)
    )


def get_mobilizon_future_events(
    page: int = 1, from_date: Optional[arrow.Arrow] = None
) -> List[MobilizonEvent]:

    url = get_settings()["source"]["mobilizon"]["url"]
    query = query_future_events.format(
        group=get_settings()["source"]["mobilizon"]["group"],
        page=page,
        afterDatetime=from_date or arrow.now().isoformat(),
    )
    r = requests.post(url, json={"query": query})
    if r.status_code != HTTPStatus.OK:
        raise MobilizonRequestFailed(
            f"Request for events failed with code:{r.status_code}"
        )

    return list(
        map(parse_event, r.json()["data"]["group"]["organizedEvents"]["elements"])
    )
