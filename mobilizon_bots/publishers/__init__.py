from mobilizon_bots.config.config import get_settings
import mobilizon_bots.config.publishers


def get_active_publishers():
    return mobilizon_bots.config.publishers.get_active_publishers(get_settings())
