from django import template
from django.conf import settings

from aa_kanban import __version__

register = template.Library()


@register.simple_tag
def kanban_version():
    """Return the installed aa-kanban version."""
    return __version__


@register.simple_tag
def kanban_app_name():
    """Return the configured app name (same as the sidebar menu item)."""
    return getattr(settings, "AA_KANBAN_APP_NAME", "Kanban")


@register.filter
def get_cards_for_column(lists, col_name):
    name_lower = col_name.lower()

    # Define mapping keywords for the 5 default columns
    mappings = {
        "backlog": ["backlog", "idea"],
        "to do": ["to do", "todo", "prompt", "ready"],
        "in progress": ["progress", "doing", "active", "generation"],
        "review/testing": ["review", "test", "edit", "verify"],
        "done": ["done", "complete", "publish", "finish"],
    }

    keywords = mappings.get(name_lower, [name_lower])

    cards = []
    for kanban_list in lists:
        list_name_lower = kanban_list.name.lower()
        if any(kw in list_name_lower for kw in keywords):
            cards.extend(list(kanban_list.cards.all()))

    return cards


@register.filter
def render_markdown(text: str):
    """Safely render Markdown to sanitized HTML."""
    if not text:
        return ""
    from django.utils.safestring import mark_safe

    from aa_kanban.markdown import render_markdown as _render_markdown

    return mark_safe(_render_markdown(text))


@register.filter
def first_image_url(text: str) -> str:
    """Return the URL of the first Markdown image in text, or "" if none."""
    from aa_kanban.markdown import extract_first_image_url

    return extract_first_image_url(text)


@register.filter
def strip_image_markdown(text: str) -> str:
    """Remove Markdown image references from text, for a text-only preview."""
    from aa_kanban.markdown import strip_image_markdown as _strip_image_markdown

    return _strip_image_markdown(text)
