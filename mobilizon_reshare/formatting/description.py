from bs4 import BeautifulSoup, Tag
import markdownify


def get_bottom_paragraphs(soup: BeautifulSoup) -> list[Tag]:
    return [d for d in soup.findAll("p") if not d.find("p")]


def html_to_plaintext(content) -> str:
    """
    Transform a HTML in a plaintext string that can be more easily processed by the publishers.

    :param content:
    :return:
    """
    # TODO: support links and quotes
    soup = BeautifulSoup(content, features="html.parser")
    p_list = get_bottom_paragraphs(soup)
    if p_list:
        return "\n".join(" ".join(tag.stripped_strings) for tag in p_list)

    return soup.text


def html_to_markdown(content) -> str:
    markdown = markdownify.markdownify(content)
    escaped_markdown = markdown.replace(">", "\\>")
    return escaped_markdown.strip()
