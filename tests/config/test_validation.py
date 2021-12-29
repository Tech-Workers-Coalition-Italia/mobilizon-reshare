import os
from unittest.mock import MagicMock

import dynaconf
import pkg_resources
import pytest

from mobilizon_reshare.config import config
from mobilizon_reshare.config.config import get_settings, CustomConfig, build_and_validate_settings
import os
from unittest.mock import MagicMock

import dynaconf
import pkg_resources
import pytest

from mobilizon_reshare.config import config
from mobilizon_reshare.config.config import get_settings, CustomConfig

@pytest.fixture
def mock_settings(toml_content, tmp_path):

    CustomConfig.clear()
    file = tmp_path / "tmp.toml"
    file.write_text(toml_content)
    old_method=config.get_settings_files_paths
    config.get_settings_files_paths = MagicMock(return_value=[file.absolute()])
    yield
    config.get_settings_files_paths=old_method
    CustomConfig.clear()


@pytest.mark.parametrize("toml_content", ["invalid toml["])
def test_get_settings_failure_invalid_toml(mock_settings, ):
    with pytest.raises(dynaconf.vendor.toml.decoder.TomlDecodeError):
        build_and_validate_settings()


@pytest.mark.parametrize("toml_content", [""])
def test_get_settings_failure_invalid_preliminary_config(mock_settings, ):
    os.environ["SECRETS_FOR_DYNACONF"] = ""

    with pytest.raises(dynaconf.validator.ValidationError):
        build_and_validate_settings()


@pytest.mark.parametrize(
    "toml_content,pattern_in_exception",
    [
        [
            open(pkg_resources.resource_filename(
                "tests.resources.config", "config_with_invalid_strategy.toml"
            )).read(),
            "break_between_events_in_minutes"]
    ],
)
def test_get_settings_failure_config_base_validators(
        mock_settings, pattern_in_exception
):

    with pytest.raises(dynaconf.validator.ValidationError) as e:
        build_and_validate_settings()
    assert e.match(pattern_in_exception)
