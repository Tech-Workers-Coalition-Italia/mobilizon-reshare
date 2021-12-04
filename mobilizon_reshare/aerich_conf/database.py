"""tortoise orm conf for aerich"""
from pathlib import Path
import toml

CONF_FILE = "mobilizon_reshare/settings.toml"

SETTINGS = toml.load(CONF_FILE)
db_path = Path(SETTINGS['default']['db_path'])

db_url = f"sqlite:///{db_path}"

TORTOISE_ORM = {
    "connections": {"default": db_url},
    "apps": {
        "models": {
            "models": ["mobilizon_reshare.models.event",
                       "mobilizon_reshare.models.notification",
                       "mobilizon_reshare.models.publication",
                       "mobilizon_reshare.models.publisher", "aerich.models"],
            "default_connection": "default",
        },
    },
}
