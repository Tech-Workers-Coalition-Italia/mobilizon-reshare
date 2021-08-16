import pytest

from mobilizon_reshare.formatting.description import html_to_plaintext


@pytest.mark.parametrize(
    "description, expected_output",
    [
        ["", ""],
        ["<p>Description</p>", "Description"],
        [
            "<p>Some description <em>abc</em></p><p></p><p><strong>Bold</strong></p><p></p>"
            "<p><em>Italic</em></p><p></p><blockquote><p>Quote</p></blockquote>",
            "Some description abc\n\nBold\n\nItalic\n\nQuote",
        ],
        ["<p><a href='https://some_link.com'>Some Link</a></p>", "Some Link"],
    ],
)
def test_html_to_plaintext(description, expected_output):
    assert html_to_plaintext(description) == expected_output
