from typing import List

from bs4 import BeautifulSoup, Tag
import markdownify


def get_bottom_paragraphs(soup: BeautifulSoup) -> List[Tag]:
    return [d for d in soup.findAll("p") if not d.find("p")]


def html_to_plaintext(content):
    """
    Transform a HTML in a plaintext sting that can be more easily processed by the publishers.

    :param content:
    :return:
    """
    # TODO: support links and quotes
    soup = BeautifulSoup(content)
    return "\n".join(
        " ".join(tag.stripped_strings) for tag in get_bottom_paragraphs(soup)
    )


def html_to_markdown(content):
    markdown = markdownify.markdownify(content)
    escaped_markdown = markdown.replace(">", "\\>")
    return escaped_markdown.strip()
