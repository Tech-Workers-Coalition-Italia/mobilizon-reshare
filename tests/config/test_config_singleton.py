import pkg_resources

from mobilizon_reshare.config.config import get_settings


def test_singleton():
    settings_file = pkg_resources.resource_filename(
        "tests.resources.config", "test_singleton.toml"
    )
    config_1 = get_settings(settings_file)
    config_2 = get_settings()
    assert id(config_1) == id(config_2)


def test_same_file():
    settings_file = pkg_resources.resource_filename(
        "tests.resources.config", "test_singleton.toml"
    )
    config_1 = get_settings(settings_file)
    config_2 = get_settings(settings_file)
    assert id(config_1) == id(config_2)


def test_singleton_new_file():
    settings_file = pkg_resources.resource_filename(
        "tests.resources.config", "test_singleton.toml"
    )
    settings_file_2 = pkg_resources.resource_filename(
        "tests.resources.config", "test_singleton_2.toml"
    )
    config_1 = get_settings(settings_file)
    config_2 = get_settings(settings_file_2)
    assert id(config_1) != id(config_2)
