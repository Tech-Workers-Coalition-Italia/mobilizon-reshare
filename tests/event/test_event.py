import pytest
from jinja2 import Template


@pytest.fixture()
def simple_template():
    return Template(
        (
            "{{name}}|{{description}}|{{location}}|{{begin_datetime.strftime('%Y-%m-%d, %H:%M')}}"
            "|{{last_update_time('%Y-%m-%d, %H:%M')}}"
        )
    )


def test_fill_template(event, simple_template):
    assert (
        event._fill_template(simple_template)
        == "test event|description of the event|location|2021-01-01, 11:30|2021-01-01, 11:30"
    )


def test_format(event, simple_template):
    assert (
        event.format(simple_template)
        == "test event|description of the event|location|2021-01-01, 11:30|2021-01-01, 11:30"
    )
