import os

import dynaconf
import pkg_resources
import pytest

from mobilizon_reshare.config.config import update_settings_files


@pytest.fixture
def invalid_settings_file(tmp_path, toml_content):
    file = tmp_path / "tmp.toml"
    file.write_text(toml_content)
    return file


@pytest.mark.parametrize("toml_content", ["invalid toml["])
def test_update_failure_invalid_toml(invalid_settings_file):
    with pytest.raises(dynaconf.vendor.toml.decoder.TomlDecodeError):
        update_settings_files(invalid_settings_file.absolute())


@pytest.mark.parametrize("toml_content", [""])
def test_update_failure_invalid_preliminary_config(invalid_settings_file):
    os.environ["SECRETS_FOR_DYNACONF"] = ""

    with pytest.raises(dynaconf.validator.ValidationError):
        update_settings_files(invalid_settings_file.absolute())


@pytest.mark.parametrize(
    "invalid_toml,pattern_in_exception",
    [["config_with_invalid_strategy.toml", "break_between_events_in_minutes"]],
)
def test_update_failure_config_base_validators(invalid_toml, pattern_in_exception):

    with pytest.raises(dynaconf.validator.ValidationError) as e:
        update_settings_files(
            pkg_resources.resource_filename("tests.resources.config", invalid_toml)
        )

    assert e.match(pattern_in_exception)


@pytest.mark.parametrize(
    "invalid_toml,pattern_in_exception",
    [
        ["empty.toml", "publisher.*.active"],
        ["config_with_invalid_telegram.toml", "token"],
    ],
)
def test_update_failure_config_all_validators(invalid_toml, pattern_in_exception):

    os.environ["SECRETS_FOR_DYNACONF"] = pkg_resources.resource_filename(
        "tests.resources.config", invalid_toml
    )

    with pytest.raises(dynaconf.validator.ValidationError) as e:
        update_settings_files(
            pkg_resources.resource_filename(
                "tests.resources.config", "test_singleton.toml"
            )
        )
    assert e.match(pattern_in_exception)
