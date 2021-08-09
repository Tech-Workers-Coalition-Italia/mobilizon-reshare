from mobilizon_reshare.config.config import get_settings
import mobilizon_reshare.config.publishers


def get_active_publishers():
    return mobilizon_reshare.config.publishers.get_active_publishers(get_settings())
