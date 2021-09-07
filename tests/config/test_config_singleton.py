import pkg_resources

from mobilizon_reshare.config.config import get_settings, update_settings_files


def test_singleton():
    settings_file = pkg_resources.resource_filename(
        "tests.resources.config", "test_singleton.toml"
    )
    config_1 = get_settings(settings_file)
    config_2 = get_settings()
    assert id(config_1) == id(config_2)


def test_singleton_update():
    settings_file = pkg_resources.resource_filename(
        "tests.resources.config", "test_singleton.toml"
    )
    config_1 = get_settings(settings_file)
    config_2 = update_settings_files(settings_file)
    config_3 = get_settings()
    assert id(config_1) != id(config_2)
    assert id(config_2) == id(config_3)
