"""Search cards across all boards a user can see (TASK-114)."""

import re

from django.contrib.auth.models import User
from django.db.models import Case, IntegerField, Q, QuerySet, Value, When

from .markdown import strip_image_markdown
from .models import Board, Card, Comment
from .permissions import user_can_manage_boards

MIN_QUERY_LENGTH = 2
MAX_TERMS = 5
RESULT_LIMIT = 100
SNIPPET_WIDTH = 120

_CARD_NUMBER = re.compile(r"^#?(\d+)$")

_TEXT_FIELDS = (
    "title",
    "description",
    "comments__text",
    "assignees__username",
    "created_by__username",
    "comments__author__username",
    "labels__name",
    "assigned_team__name",
)


def search_terms(query: str) -> list[str]:
    """Split a query into at most MAX_TERMS words; empty when it is too short."""
    query = (query or "").strip()
    if len(query) < MIN_QUERY_LENGTH and not _CARD_NUMBER.match(query):
        return []
    return query.split()[:MAX_TERMS]


def searchable_boards(user: User) -> QuerySet[Board]:
    """Boards the user may open, by the same rules as Board.can_user_view."""
    boards = Board.objects.visible_to(user)
    if user.is_superuser:
        return boards
    if user_can_manage_boards(user):
        # Managers open every archived board, also without a group on it.
        return Board.objects.filter(
            Q(pk__in=boards.values("pk")) | Q(is_archived=True)
        ).distinct()
    return boards.filter(Q(is_archived=False) | Q(created_by=user))


def _first_hit(text: str, terms: list[str]) -> int:
    lowered = text.lower()
    hits = [lowered.find(term.lower()) for term in terms]
    hits = [h for h in hits if h >= 0]
    return min(hits) if hits else -1


def snippet(text: str, terms: list[str], width: int = SNIPPET_WIDTH) -> str:
    """Plain text around the first matching term, or "" without a match."""
    plain = " ".join(strip_image_markdown(text or "").split())
    hit = _first_hit(plain, terms)
    if hit < 0:
        return ""
    start = max(0, hit - width // 3)
    end = min(len(plain), start + width)
    return ("…" if start else "") + plain[start:end] + ("…" if end < len(plain) else "")


def _attach_snippets(cards: list[Card], terms: list[str]) -> None:
    """Give each card without a title match a `snippet` from its text or comments."""
    need = [c for c in cards if _first_hit(c.title, terms) < 0]
    comment_text: dict[int, str] = {}
    pending = [c.pk for c in need if not snippet(c.description, terms)]
    if pending:
        match = Q()
        for term in terms:
            match |= Q(text__icontains=term)
        for card_id, text in (
            Comment.objects.filter(match, card__in=pending)
            .order_by("-created_at")
            .values_list("card_id", "text")
        ):
            comment_text.setdefault(card_id, text)
    for card in cards:
        card.snippet = ""
    for card in need:
        card.snippet = snippet(card.description, terms) or snippet(
            comment_text.get(card.pk, ""), terms
        )


def _term_filter(term: str) -> Q:
    condition = Q()
    for field in _TEXT_FIELDS:
        condition |= Q(**{f"{field}__icontains": term})
    number = _CARD_NUMBER.match(term)
    if number:
        condition |= Q(pk=int(number.group(1)))
    return condition


def search_cards(
    user: User,
    query: str,
    include_archived: bool = False,
    limit: int = RESULT_LIMIT,
) -> tuple[list[Card], bool]:
    """Return (cards, truncated): matching cards the user may see, best first.

    Every word must match somewhere on the card. On boards that show a reader
    only their own cards, only those cards are searched.
    """
    terms = search_terms(query)
    if not terms:
        return [], False

    boards = list(searchable_boards(user))
    full_view = [b.pk for b in boards if b.can_user_see_all_cards(user)]
    own_only = [b.pk for b in boards if b.pk not in set(full_view)]

    access = Q(list__board__in=full_view)
    if own_only:
        access |= Q(
            list__board__in=own_only,
            pk__in=Card.objects.owned_by(user).values("pk"),
        )

    cards = Card.objects.filter(access)
    if not include_archived:
        cards = cards.filter(is_archived=False)
    for term in terms:
        cards = cards.filter(_term_filter(term))

    title_hit = Q()
    for term in terms:
        title_hit |= Q(title__icontains=term)
    title_match = Case(
        When(title_hit, then=Value(1)), default=Value(0), output_field=IntegerField()
    )

    # Rank first, then cut: the best matches survive the limit.
    ranked = (
        cards.annotate(title_match=title_match)
        .order_by("-title_match", "-updated_at", "-pk")
        .values_list("pk", "title_match", "updated_at")
        .distinct()[: limit + 1]
    )
    ids = [row[0] for row in ranked]
    truncated = len(ids) > limit
    ids = ids[:limit]

    by_id = {
        card.pk: card
        for card in Card.objects.filter(pk__in=ids)
        .select_related("list__board", "created_by", "assigned_team")
        .prefetch_related("assignees", "labels")
    }
    results = [by_id[pk] for pk in ids if pk in by_id]
    _attach_snippets(results, terms)
    return results, truncated
