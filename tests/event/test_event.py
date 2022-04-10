import pytest
from jinja2 import Template

from mobilizon_reshare.config.config import get_settings


@pytest.fixture()
def set_locale(locale):
    settings = get_settings()
    old_locale = settings["locale"]
    yield get_settings().update({"locale": locale})
    settings.update({"locale": old_locale})


@pytest.fixture()
def simple_template():
    return Template(
        (
            "{{name}}|{{description}}|{{location}}|{{begin_datetime.strftime('%Y-%m-%d, %H:%M')}}"
            "|{{end_datetime.strftime('%Y-%m-%d, %H:%M')}}"
        )
    )


@pytest.fixture()
def template_with_locale():
    return Template(
        (
            "{{name}}|{{description}}|{{location}}|{{begin_datetime.format('DD MMMM, HH:mm', locale=locale)}}"
            "|{{end_datetime.format('DD MMMM, HH:mm', locale=locale)}}"
        )
    )


def test_fill_template(event, simple_template):
    assert (
        event._fill_template(simple_template)
        == "test event|description of the event|location|2021-01-01, 11:30|2021-01-01, 12:30"
    )


def test_format(event, simple_template):
    assert (
        event.format(simple_template)
        == "test event|description of the event|location|2021-01-01, 11:30|2021-01-01, 12:30"
    )


@pytest.mark.parametrize("locale", ["it-it"])
def test_locale(event, template_with_locale, set_locale):

    assert (
        event.format(template_with_locale)
        == "test event|description of the event|location|01 gennaio, 11:30|01 gennaio, 12:30"
    )
