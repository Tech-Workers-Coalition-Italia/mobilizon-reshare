from typing import List, Optional

import arrow
import requests

from mobilizon_bots.config.config import settings
from mobilizon_bots.event.event import MobilizonEvent, PublicationStatus


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
        last_accessed=arrow.now(),
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


def get_mobilizon_future_events(
    page: int = 1, from_date: Optional[arrow.Arrow] = None
) -> List[MobilizonEvent]:

    url = settings["source"]["mobilizon"]["url"]
    query = query_future_events.format(
        group="test", page=page, afterDatetime=from_date or arrow.now().isoformat()
    )
    r = requests.post(url, json={"query": query})
    return list(
        map(parse_event, r.json()["data"]["group"]["organizedEvents"]["elements"])
    )
