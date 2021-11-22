from mobilizon_reshare.config.config import get_settings
from mobilizon_reshare.storage.query.write import update_publishers


async def setup_publishers(publisher_names: list[str]):
    settings = get_settings()
    for publisher in settings["publisher"].keys():
        settings["publisher"][publisher]["active"] = publisher in publisher_names

    await update_publishers(publisher_names)
