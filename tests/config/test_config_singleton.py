import dynaconf
import pkg_resources
import pytest

from mobilizon_bots.config.config import get_settings, update_settings_files


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


@pytest.fixture
def invalid_settings_file(tmp_path, toml_content):
    file = tmp_path / "tmp.toml"
    file.write_text(toml_content)
    return file


@pytest.mark.parametrize("toml_content", ["invalid toml["])
def test_update_failure_invalid_toml(invalid_settings_file):
    with pytest.raises(dynaconf.vendor.toml.decoder.TomlDecodeError):
        update_settings_files([invalid_settings_file.absolute()])


@pytest.mark.parametrize("toml_content", [""])
def test_update_failure_invalid_preliminary_config(invalid_settings_file):
    with pytest.raises(dynaconf.validator.ValidationError):
        update_settings_files([invalid_settings_file.absolute()])


@pytest.mark.parametrize(
    "invalid_toml",
    [pkg_resources.resource_filename("resources.config", "config_with_strategy.toml")],
)
def test_update_failure_config_without_publishers(invalid_toml):
    with pytest.raises(dynaconf.validator.ValidationError) as e:
        update_settings_files([invalid_toml])
    assert e.match("publisher.*.active")


@pytest.mark.parametrize(
    "invalid_toml",
    [
        pkg_resources.resource_filename(
            "resources.config", "config_with_preliminary.toml"
        )
    ],
)
def test_update_failure_config_with_only_preliminary(invalid_toml):
    with pytest.raises(dynaconf.validator.ValidationError) as e:
        update_settings_files([invalid_toml])

    assert e.match("publishing.window.begin")
