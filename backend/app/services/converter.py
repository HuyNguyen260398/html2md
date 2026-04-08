import re

import html2text
from bs4 import BeautifulSoup, Comment


_PRESERVE_WHITESPACE_TAGS = {"pre", "code", "textarea"}


def _clean_html(html: str) -> str:
    """Strip scripts, styles, and other noisy tags before conversion."""
    soup = BeautifulSoup(html, "lxml")

    # Remove tags whose content should not appear in Markdown output.
    for tag in soup.find_all(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    # Remove HTML comments.
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Collapse inline newlines inside text nodes (outside pre/code blocks).
    # HTML rendering ignores these — they become spaces — but html2text would
    # otherwise pass them through as literal \n in the Markdown output.
    for node in soup.find_all(string=True):
        if isinstance(node, Comment):
            continue
        if any(p.name in _PRESERVE_WHITESPACE_TAGS for p in node.parents):
            continue
        normalized = re.sub(r"\s*\n\s*", " ", str(node))
        if normalized != str(node):
            node.replace_with(normalized)

    return str(soup)


def _normalise_markdown(md: str) -> str:
    """Strip leading/trailing whitespace and collapse excess blank lines."""
    md = md.strip()
    # Collapse 3+ consecutive blank lines down to 2.
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md


def convert_html_to_markdown(html: str) -> str:
    """Convert an HTML string to clean Markdown."""
    cleaned = _clean_html(html)

    converter = html2text.HTML2Text()
    converter.body_width = 0          # No hard line wrapping.
    converter.protect_links = True    # Wrap links so they survive re-conversion.
    converter.unicode_snob = True     # Use Unicode instead of ASCII approximations.
    converter.ignore_images = False   # Keep image references.
    converter.ignore_links = False    # Keep hyperlinks.
    converter.bypass_tables = False   # Render tables as Markdown tables.

    raw_md = converter.handle(cleaned)
    return _normalise_markdown(raw_md)
