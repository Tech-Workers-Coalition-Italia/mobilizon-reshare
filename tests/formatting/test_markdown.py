import pytest

from mobilizon_bots.formatting.description import html_to_markdown


@pytest.mark.parametrize(
    "description, expected_output",
    [
        ["", ""],
        ["<p>Description</p>", "Description"],
        [
            "<p>Some description <em>abc</em></p><p></p><p><strong>Bold</strong></p><p></p>"
            "<p><em>Italic</em></p><p></p><blockquote><p>Quote</p></blockquote>",
            """Some description *abc*\n\n**Bold**\n\n*Italic*\n\n\n\\> Quote\n\\> \n\\>""",
        ],
        [
            "<p><a href='https://some_link.com'>Some Link</a></p>",
            "[Some Link](https://some_link.com)",
        ],
    ],
)
def test_html_to_markdown(description, expected_output):
    assert html_to_markdown(description) == expected_output
