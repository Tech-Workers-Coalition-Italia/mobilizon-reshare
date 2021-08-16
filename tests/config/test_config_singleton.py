from mobilizon_reshare.config.config import get_settings, update_settings_files


def test_singleton():
    config_1 = get_settings()
    config_2 = get_settings()
    assert id(config_1) == id(config_2)


def test_singleton_update():
    config_1 = get_settings()
    config_2 = update_settings_files([])
    config_3 = get_settings()
    assert id(config_1) != id(config_2)
    assert id(config_2) == id(config_3)
