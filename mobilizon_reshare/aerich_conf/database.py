"""tortoise orm conf for aerich"""
from pathlib import Path
from mobilizon_reshare.config.config import get_settings

CONF_FILE = "settings.toml"

SETTINGS = get_settings(CONF_FILE)
db_path = Path(SETTINGS.db_path)

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
