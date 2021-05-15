from typing import List

from mobilizon_bots.event.event import MobilizonEvent
import requests
import arrow

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
                  attributedTo {{
                    avatar {{
                      url,
                    }}
                    name,
                    preferredUsername,
                  }},
                  description,
                  onlineAddress,
                  physicalAddress {{
                    locality,
                    description,
                    region
                  }},
                  tags {{
                    title,
                    id,
                    slug
                  }},
                  picture {{
                    url
                    }},
                }},
              }}
            }}
          }}"""


def get_mobilizon_future_events() -> List[MobilizonEvent]:
    url = "https://apero.bzh/api"
    query = query_future_events.format(
        group="test", page=1, afterDatetime=arrow.now().isoformat()
    )

    r = requests.post(url, json={"query": query})
    return r.json()


get_mobilizon_future_events()
