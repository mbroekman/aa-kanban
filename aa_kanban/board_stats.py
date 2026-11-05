"""Per-board card counts and attention signals for the board overview."""

from dataclasses import dataclass, field
from datetime import timedelta

from django.db.models import Max
from django.utils import timezone

from .models import Board, Card, List

# List names that mean "finished", as for stale card alerts.
DONE_KEYWORDS = ("done", "afgerond", "completed", "closed", "gesloten")


@dataclass
class BoardStats:
    card_count: int = 0
    overdue: int = 0
    inactive: int = 0
    over_wip: list[str] = field(default_factory=list)

    @property
    def needs_attention(self) -> bool:
        return bool(self.overdue or self.inactive or self.over_wip)


def is_done_list(lst: List, last_list_id: int | None) -> bool:
    name = lst.name.lower()
    return lst.id == last_list_id or any(kw in name for kw in DONE_KEYWORDS)


def board_stats(boards: list[Board]) -> dict[int, BoardStats]:
    """Stats per board id, in two queries whatever the number of boards.

    A card needs attention when it is not archived, not in a finished
    list, and either past its due date or inactive (no update or comment)
    longer than the board's stale_card_alert_hours. A column needs attention
    when it holds more cards than its WIP limit.
    """
    stats = {b.id: BoardStats() for b in boards}
    if not stats:
        return stats
    alert_hours = {b.id: b.stale_card_alert_hours for b in boards}

    lists = List.objects.filter(board_id__in=stats).order_by("board_id", "order", "id")
    last_list_ids: dict[int, int] = {}
    for lst in lists:
        last_list_ids[lst.board_id] = lst.id  # ordered, so the last one wins
    list_by_id = {lst.id: lst for lst in lists}
    done_ids = {
        lst.id for lst in lists if is_done_list(lst, last_list_ids.get(lst.board_id))
    }

    now = timezone.now()
    cards = (
        Card.objects.filter(list__board_id__in=stats, is_archived=False)
        .annotate(last_comment=Max("comments__created_at"))
        .values("list_id", "due_date", "updated_at", "last_comment")
    )
    per_list: dict[int, int] = {}
    for card in cards:
        lst = list_by_id[card["list_id"]]
        board = stats[lst.board_id]
        board.card_count += 1
        per_list[lst.id] = per_list.get(lst.id, 0) + 1
        if lst.id in done_ids:
            continue
        if card["due_date"] and card["due_date"] < now:
            board.overdue += 1
        hours = alert_hours[lst.board_id]
        if hours:
            last_activity = max(
                filter(None, (card["updated_at"], card["last_comment"]))
            )
            if last_activity < now - timedelta(hours=hours):
                board.inactive += 1

    for lst in lists:
        if lst.wip_limit and per_list.get(lst.id, 0) > lst.wip_limit:
            stats[lst.board_id].over_wip.append(lst.name)
    return stats
