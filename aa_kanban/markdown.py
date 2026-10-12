"""Safe Markdown rendering and image enhancement for aa_kanban."""

import logging
import re
import urllib.parse
from bs4 import BeautifulSoup
import markdown

logger = logging.getLogger(__name__)

ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "del",
    "strike",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "code",
    "pre",
    "hr",
    "a",
    "img",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
}

ALLOWED_ATTRS = {
    "a": {"href", "title", "target", "rel"},
    "img": {"src", "alt", "title", "class", "loading", "style", "data-image-zoom"},
    "th": {"align"},
    "td": {"align"},
}


def _is_safe_url(url: str) -> bool:
    """Validate that the given URL does not use dangerous protocols like javascript:."""
    if not url:
        return False
    # Strip leading whitespace and control characters
    url_cleaned = re.sub(r"[\x00-\x20]+", "", url)
    parsed = urllib.parse.urlparse(url_cleaned)
    # Allow relative URLs and safe http/https schemes
    if parsed.scheme.lower() in ("", "http", "https"):
        return True
    return False


def render_markdown(text: str) -> str:
    """Safely render Markdown into sanitized HTML with enhanced image handling.

    - Converts Markdown to HTML with fenced code blocks, tables, and linebreaks.
    - Strips all disallowed HTML tags and malicious attributes (e.g. onerror, onload).
    - Enforces safe URLs for links and images (blocks javascript: and dangerous schemes).
    - Enhances <img> tags with responsive Bootstrap classes, lazy loading, and lightbox hooks.
    """
    if not text or not text.strip():
        return ""

    try:
        raw_html = markdown.markdown(
            text,
            extensions=["fenced_code", "tables", "nl2br"],
        )
    except Exception as e:
        logger.warning(f"Markdown rendering error: {e}")
        from django.utils.html import escape, linebreaks

        return linebreaks(escape(text))

    try:
        soup = BeautifulSoup(raw_html, "html.parser")

        # Sanitize elements
        for tag in soup.find_all(True):
            if tag.name.lower() not in ALLOWED_TAGS:
                tag.decompose()
                continue

            allowed_attrs = ALLOWED_ATTRS.get(tag.name.lower(), set())
            attrs = dict(tag.attrs)
            for attr in attrs:
                if attr.lower() not in allowed_attrs:
                    del tag[attr]

            if tag.name.lower() == "a":
                href = tag.get("href", "")
                if not _is_safe_url(href):
                    tag["href"] = "#"
                tag["target"] = "_blank"
                tag["rel"] = "noopener noreferrer"

            elif tag.name.lower() == "img":
                src = tag.get("src", "")
                if not _is_safe_url(src):
                    tag.decompose()
                    continue

                existing_classes = tag.get("class", [])
                if isinstance(existing_classes, str):
                    existing_classes = existing_classes.split()
                classes = set(existing_classes) | {
                    "img-fluid",
                    "rounded",
                    "kanban-rendered-image",
                }
                tag["class"] = sorted(list(classes))
                tag["loading"] = "lazy"
                tag["data-image-zoom"] = "true"
                tag["style"] = "max-height: 400px; cursor: zoom-in; object-fit: contain;"

            elif tag.name.lower() == "table":
                tag["class"] = ["table", "table-sm", "table-bordered", "my-2"]

        return str(soup)
    except Exception as e:
        logger.warning(f"Sanitization error in markdown: {e}")
        from django.utils.html import escape, linebreaks

        return linebreaks(escape(text))
