"""JSON API views for the aa_kanban React/shadcn SPA."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group as AuthGroup, User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Prefetch, Q, prefetch_related_objects
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

from .board_stats import board_stats
from .markdown import render_markdown
from .models import (
    Board,
    Card,
    Comment,
    KanbanGroup,
    KanbanSetting,
    KanbanTeam,
    Label,
    List,
)
from .permissions import manage_boards_required, user_can_manage_boards
from .search import RESULT_LIMIT, search_cards


def _json_body(request: HttpRequest) -> dict[str, Any]:
    """Parse JSON request body into a dictionary."""
    if not request.body:
        return {}
    try:
        data = json.loads(request.body)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _serialize_user(user: User | None) -> dict[str, Any] | None:
    """Serialize a User to minimal public display data."""
    if user is None:
        return None
    return {
        "id": user.pk,
        "username": user.username,
    }


def _serialize_label(label: Label) -> dict[str, Any]:
    """Serialize a Label."""
    return {
        "id": label.pk,
        "name": label.name,
        "color": label.color,
        "is_ticket_label": label.is_ticket_label,
    }


def _serialize_team(team: KanbanTeam) -> dict[str, Any]:
    """Serialize a KanbanTeam."""
    return {
        "id": team.pk,
        "name": team.name,
    }


def _serialize_card(card: Card, include_comments: bool = False) -> dict[str, Any]:
    """Serialize a Card with labels, assignees, and optional comments."""
    comment_count = getattr(card, "comment_count", None)
    if comment_count is None:
        comment_count = card.comments.count()

    data: dict[str, Any] = {
        "id": card.pk,
        "list_id": card.list_id,
        "title": card.title,
        "description": card.description,
        "description_html": (
            render_markdown(card.description) if card.description else ""
        ),
        "order": card.order,
        "color": card.color,
        "due_date": card.due_date.isoformat() if card.due_date else None,
        "is_archived": card.is_archived,
        "created_by": _serialize_user(card.created_by),
        "created_at": card.created_at.isoformat(),
        "updated_at": card.updated_at.isoformat(),
        "assigned_team": (
            _serialize_team(card.assigned_team) if card.assigned_team else None
        ),
        "labels": [_serialize_label(lbl) for lbl in card.labels.all()],
        "assignees": [_serialize_user(u) for u in card.assignees.all()],
        "comment_count": comment_count,
        "discord_thread_id": card.discord_thread_id,
    }
    if include_comments:
        data["comments"] = [
            {
                "id": c.pk,
                "author": _serialize_user(c.author),
                "text": c.text,
                "text_html": render_markdown(c.text),
                "created_at": c.created_at.isoformat(),
            }
            for c in card.comments.select_related("author").order_by("created_at")
        ]
    return data


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_GET
def api_boards(request: HttpRequest) -> JsonResponse:
    """Return all visible active boards and user permissions."""
    boards = list(
        Board.objects.visible_to(request.user)
        .active()
        .select_related("created_by")
        .prefetch_related("view_groups", "write_groups")
        .annotate(list_count=Count("lists", distinct=True))
    )
    stats = board_stats(boards, request.user)
    can_manage = user_can_manage_boards(request.user)

    serialized_boards = []
    for board in boards:
        b_stats = stats[board.pk]
        serialized_boards.append(
            {
                "id": board.pk,
                "name": board.name,
                "slug": board.slug,
                "description": board.description,
                "is_members_board": board.is_members_board,
                "is_ticket_board": board.is_ticket_board,
                "own_cards_only": board.own_cards_only,
                "list_count": board.list_count,
                "card_count": b_stats.card_count,
                "attention_count": (
                    b_stats.overdue + b_stats.inactive + len(b_stats.over_wip)
                ),
                "can_write": board.can_user_write(request.user),
                "updated_at": board.updated_at.isoformat(),
            }
        )

    return JsonResponse(
        {
            "boards": serialized_boards,
            "can_manage": can_manage,
            "can_create_ticket": request.user.has_perm("aa_kanban.create_ticket"),
            "archived_count": (
                Board.objects.filter(is_archived=True).count() if can_manage else 0
            ),
            "all_groups": (
                [
                    {"id": g.pk, "name": g.name}
                    for g in KanbanGroup.objects.order_by("name")
                ]
                if can_manage
                else []
            ),
            "user": _serialize_user(request.user),
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_GET
def api_board_detail(request: HttpRequest, board_slug: str) -> JsonResponse:
    """Return full board state: metadata, lists, visible cards, labels, teams, users."""
    board = get_object_or_404(Board, slug=board_slug)
    if not board.can_user_view(request.user):
        raise PermissionDenied("You do not have permission to view this board.")

    can_write = board.can_user_write(request.user)
    can_manage = user_can_manage_boards(request.user)

    lists_qs = board.lists.order_by("order", "id")
    cards_qs = (
        board.visible_cards(
            Card.objects.filter(list__board=board, is_archived=False),
            request.user,
        )
        .select_related("created_by", "assigned_team", "list")
        .prefetch_related("labels", "assignees")
        .annotate(comment_count=Count("comments", distinct=True))
        .order_by("order", "id")
    )

    lists_data = [
        {
            "id": lst.pk,
            "name": lst.name,
            "description": lst.description,
            "wip_limit": lst.wip_limit,
            "order": lst.order,
            "can_add_card": board.can_user_add_card(request.user, lst),
        }
        for lst in lists_qs
    ]

    cards_data = [_serialize_card(card) for card in cards_qs]

    available_labels = [_serialize_label(lbl) for lbl in Label.objects.order_by("name")]
    available_teams = [
        _serialize_team(team) for team in KanbanTeam.objects.order_by("name")
    ]
    available_users = [
        _serialize_user(u)
        for u in User.objects.filter(is_active=True).order_by("username")[:200]
    ]

    return JsonResponse(
        {
            "board": {
                "id": board.pk,
                "name": board.name,
                "slug": board.slug,
                "description": board.description,
                "is_archived": board.is_archived,
                "is_members_board": board.is_members_board,
                "is_ticket_board": board.is_ticket_board,
                "own_cards_only": board.own_cards_only,
                "discord_ticket_channel_id": board.discord_ticket_channel_id,
                "discord_alert_channel_id": board.discord_alert_channel_id,
                "discord_alert_webhook": board.discord_alert_webhook or "",
                "discord_webhook_cards": board.discord_webhook_cards or "",
                "stale_card_alert_hours": board.stale_card_alert_hours,
                "stale_card_repeat_hours": board.stale_card_repeat_hours,
                "archive_after_days": board.archive_after_days,
                "view_group_ids": list(board.view_groups.values_list("pk", flat=True)),
                "write_group_ids": list(
                    board.write_groups.values_list("pk", flat=True)
                ),
                "can_write": can_write,
                "can_manage": can_manage,
            },
            "lists": lists_data,
            "cards": cards_data,
            "labels": available_labels,
            "teams": available_teams,
            "users": available_users,
            "all_groups": (
                [
                    {"id": g.pk, "name": g.name}
                    for g in KanbanGroup.objects.order_by("name")
                ]
                if can_manage
                else []
            ),
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_create_list(request: HttpRequest, board_slug: str) -> JsonResponse:
    """Create a new column on the board."""
    board = get_object_or_404(Board, slug=board_slug)
    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required for this board.")

    data = _json_body(request)
    name = str(data.get("name", "")).strip()
    if not name:
        return JsonResponse({"error": _("Column name is required.")}, status=400)

    wip_limit_raw = data.get("wip_limit", 0)
    try:
        wip_limit = max(0, int(wip_limit_raw))
    except (ValueError, TypeError):
        wip_limit = 0

    description = str(data.get("description", "")).strip()
    max_order = board.lists.count()
    lst = List.objects.create(
        board=board,
        name=name[:100],
        description=description,
        wip_limit=wip_limit,
        order=max_order,
    )
    return JsonResponse(
        {
            "list": {
                "id": lst.pk,
                "name": lst.name,
                "description": lst.description,
                "wip_limit": lst.wip_limit,
                "order": lst.order,
                "can_add_card": True,
            }
        },
        status=201,
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_create_card(request: HttpRequest, list_id: int) -> JsonResponse:
    """Create a new card in a list and return it as JSON."""
    kanban_list = get_object_or_404(List.objects.select_related("board"), pk=list_id)
    board = kanban_list.board
    if not board.can_user_add_card(request.user, kanban_list):
        raise PermissionDenied("You do not have permission to add cards here.")

    data = _json_body(request)
    title = str(data.get("title", "")).strip()
    if not title:
        return JsonResponse({"error": _("Card title is required.")}, status=400)

    if kanban_list.wip_limit > 0:
        active_count = kanban_list.cards.filter(is_archived=False).count()
        if active_count >= kanban_list.wip_limit:
            return JsonResponse(
                {"error": _("This column has reached its WIP limit.")}, status=400
            )

    description = str(data.get("description", "")).strip()
    order = kanban_list.cards.filter(is_archived=False).count()
    card = Card.objects.create(
        list=kanban_list,
        title=title[:255],
        description=description,
        order=order,
        created_by=request.user,
        moved_to_list_at=timezone.now(),
    )
    card = (
        Card.objects.select_related("created_by", "assigned_team", "list")
        .prefetch_related("labels", "assignees")
        .get(pk=card.pk)
    )
    return JsonResponse({"card": _serialize_card(card)}, status=201)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_GET
def api_card_detail(request: HttpRequest, card_id: int) -> JsonResponse:
    """Return full card details including comments."""
    card = get_object_or_404(
        Card.objects.select_related(
            "list__board", "created_by", "assigned_team"
        ).prefetch_related("labels", "assignees"),
        pk=card_id,
    )
    board = card.list.board
    if not board.can_user_view(request.user):
        raise PermissionDenied("You do not have permission to view this card.")
    if not board.can_user_see_all_cards(request.user) and not card.is_owned_by(
        request.user
    ):
        raise PermissionDenied("You do not have permission to view this card.")

    return JsonResponse({"card": _serialize_card(card, include_comments=True)})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_update_card(request: HttpRequest, card_id: int) -> JsonResponse:
    """Update card fields (title, description, color, due_date, team, labels)."""
    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    board = card.list.board
    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required for this board.")

    data = _json_body(request)
    update_fields: list[str] = ["updated_at"]

    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return JsonResponse({"error": _("Card title cannot be empty.")}, status=400)
        card.title = title[:255]
        update_fields.append("title")

    if "description" in data:
        card.description = str(data["description"])
        update_fields.append("description")

    if "color" in data:
        valid_colors = {c[0] for c in Card.COLOR_CHOICES}
        color = str(data["color"])
        if color in valid_colors:
            card.color = color
            update_fields.append("color")

    if "due_date" in data:
        raw_due = data["due_date"]
        if not raw_due:
            card.due_date = None
            update_fields.append("due_date")
        else:
            parsed: datetime | None = parse_datetime(str(raw_due))
            if parsed is None:
                try:
                    parsed = datetime.fromisoformat(str(raw_due))
                except ValueError:
                    return JsonResponse(
                        {"error": _("Invalid due date format.")}, status=400
                    )
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
            card.due_date = parsed
            update_fields.append("due_date")

    if "assigned_team_id" in data:
        team_id = data["assigned_team_id"]
        if team_id is None or team_id == "":
            card.assigned_team = None
        else:
            card.assigned_team = get_object_or_404(KanbanTeam, pk=int(team_id))
        update_fields.append("assigned_team")

    with transaction.atomic():
        card.save(update_fields=list(set(update_fields)))
        if "label_ids" in data and isinstance(data["label_ids"], list):
            labels = Label.objects.filter(pk__in=data["label_ids"])
            card.labels.set(labels)
        if "assignee_ids" in data and isinstance(data["assignee_ids"], list):
            users = User.objects.filter(pk__in=data["assignee_ids"])
            card.assignees.set(users)

    card = (
        Card.objects.select_related("created_by", "assigned_team", "list")
        .prefetch_related("labels", "assignees")
        .get(pk=card.pk)
    )
    return JsonResponse({"card": _serialize_card(card, include_comments=True)})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_move_card(request: HttpRequest, card_id: int) -> JsonResponse:
    """Move a card to a target list and position."""
    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    board = card.list.board
    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required for this board.")

    data = _json_body(request)
    try:
        target_list_id = int(data["target_list_id"])
        new_position = int(data.get("new_position", 0))
    except (KeyError, ValueError, TypeError):
        return JsonResponse(
            {"error": _("Invalid target_list_id or new_position.")}, status=400
        )

    target_list = get_object_or_404(List, pk=target_list_id)
    if target_list.board_id != board.pk:
        return JsonResponse(
            {"error": _("Target list does not belong to the same board.")}, status=400
        )

    source_list = card.list
    if source_list.pk != target_list.pk and target_list.wip_limit > 0:
        if target_list.cards.filter(is_archived=False).count() >= target_list.wip_limit:
            return JsonResponse(
                {"error": _("Target list has reached its WIP limit.")}, status=400
            )

    with transaction.atomic():
        target_cards = list(
            target_list.cards.filter(is_archived=False)
            .exclude(pk=card.pk)
            .order_by("order", "id")
        )
        clamped_pos = max(0, min(new_position, len(target_cards)))
        target_cards.insert(clamped_pos, card)

        for idx, c in enumerate(target_cards):
            if c.pk == card.pk:
                c.list = target_list
                c.order = idx
                fields = ["list", "order", "updated_at"]
                if source_list.pk != target_list.pk:
                    c.moved_to_list_at = timezone.now()
                    fields.append("moved_to_list_at")
                c.save(update_fields=fields)
            elif c.order != idx:
                c.order = idx
                c.save(update_fields=["order"])

        if source_list.pk != target_list.pk:
            source_cards = list(
                source_list.cards.filter(is_archived=False)
                .exclude(pk=card.pk)
                .order_by("order", "id")
            )
            for idx, c in enumerate(source_cards):
                if c.order != idx:
                    c.order = idx
                    c.save(update_fields=["order"])

    thread_closed = False
    if source_list.pk != target_list.pk:
        from aa_kanban.tasks import notify_card_creator

        creator_msg = _(
            "Your card **{card_title}** was moved from `{source_list_name}` to "
            "`{target_list_name}` by **{username}**."
        ).format(
            card_title=card.title,
            source_list_name=source_list.name,
            target_list_name=target_list.name,
            username=request.user.username,
        )
        notify_card_creator(card, str(creator_msg), actor=request.user)

        if card.discord_thread_id:
            from aa_kanban.tasks import dispatch_ticket_thread_move

            thread_msg = _(
                "🔄 **Status Update:** Card moved from `{source_list_name}` to "
                "`{target_list_name}` by **{username}**."
            ).format(
                source_list_name=source_list.name,
                target_list_name=target_list.name,
                username=request.user.username,
            )
            thread_closed = dispatch_ticket_thread_move(
                card, target_list, str(thread_msg)
            )

        if board.discord_webhook_cards:
            from aa_kanban.utils import send_discord_webhook

            url = request.build_absolute_uri(
                redirect("aa_kanban:board_detail", board_slug=board.slug).url
            )
            msg = _(
                "Card moved: **{card_title}** was moved from `{source_list_name}` to "
                "`{target_list_name}`.\n[View Board]({url})"
            ).format(
                card_title=card.title,
                source_list_name=source_list.name,
                target_list_name=target_list.name,
                url=url,
            )
            send_discord_webhook(board.discord_webhook_cards, msg)

    return JsonResponse({"ok": True, "thread_closed": thread_closed})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_close_card_thread(request: HttpRequest, card_id: int) -> JsonResponse:
    """Archive and lock a card's Discord thread."""
    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to close this thread.")

    if not card.discord_thread_id:
        return JsonResponse(
            {"error": _("This card has no Discord thread.")}, status=400
        )

    from aa_kanban.tasks import close_ticket_thread

    close_ticket_thread.delay(card.discord_thread_id)

    return JsonResponse({"ok": True})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_delete_card(request: HttpRequest, card_id: int) -> JsonResponse:
    """Delete a card."""
    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required for this board.")
    card.delete()
    return JsonResponse({"ok": True})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_add_comment(request: HttpRequest, card_id: int) -> JsonResponse:
    """Add a comment to a card."""
    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    board = card.list.board
    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required for this board.")

    data = _json_body(request)
    text = str(data.get("text", "")).strip()
    if not text:
        return JsonResponse({"error": _("Comment text cannot be empty.")}, status=400)

    comment = Comment.objects.create(card=card, author=request.user, text=text)
    return JsonResponse(
        {
            "comment": {
                "id": comment.pk,
                "author": _serialize_user(comment.author),
                "text": comment.text,
                "text_html": render_markdown(comment.text),
                "created_at": comment.created_at.isoformat(),
            }
        },
        status=201,
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_GET
def api_search(request: HttpRequest) -> JsonResponse:
    """Search cards across visible boards."""
    query = request.GET.get("q", "").strip()
    include_archived = request.GET.get("archived") == "1"
    cards, truncated = search_cards(request.user, query, include_archived)
    return JsonResponse(
        {
            "results": [
                {
                    "id": c.pk,
                    "title": c.title,
                    "board_name": c.list.board.name,
                    "board_slug": c.list.board.slug,
                    "list_name": c.list.name,
                    "is_archived": c.is_archived,
                    "labels": [_serialize_label(lbl) for lbl in c.labels.all()],
                }
                for c in cards
            ],
            "truncated": truncated,
            "limit": RESULT_LIMIT,
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_create_board(request: HttpRequest) -> JsonResponse:
    """Create a new Kanban board."""
    data = _json_body(request)
    name = str(data.get("name", "")).strip()
    if not name:
        return JsonResponse({"error": _("Board name is required.")}, status=400)

    def _opt_int(val: Any) -> int | None:
        if val is None or val == "":
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    with transaction.atomic():
        board = Board.objects.create(
            name=name[:255],
            description=str(data.get("description", "")).strip(),
            is_ticket_board=bool(data.get("is_ticket_board", False)),
            is_members_board=bool(data.get("is_members_board", False)),
            own_cards_only=bool(data.get("own_cards_only", False)),
            discord_ticket_channel_id=_opt_int(data.get("discord_ticket_channel_id")),
            discord_alert_channel_id=_opt_int(data.get("discord_alert_channel_id")),
            discord_alert_webhook=(
                str(data.get("discord_alert_webhook", "")).strip() or None
            ),
            discord_webhook_cards=(
                str(data.get("discord_webhook_cards", "")).strip() or None
            ),
            stale_card_alert_hours=max(
                0, _opt_int(data.get("stale_card_alert_hours")) or 0
            ),
            stale_card_repeat_hours=max(
                0, _opt_int(data.get("stale_card_repeat_hours")) or 24
            ),
            archive_after_days=max(0, _opt_int(data.get("archive_after_days")) or 0),
            created_by=request.user,
        )
        view_ids = data.get("view_group_ids")
        if isinstance(view_ids, list):
            board.view_groups.set(KanbanGroup.objects.filter(pk__in=view_ids))
        write_ids = data.get("write_group_ids")
        if isinstance(write_ids, list):
            board.write_groups.set(KanbanGroup.objects.filter(pk__in=write_ids))

    settings_obj = KanbanSetting.get_settings()
    if settings_obj.board_creation_webhook:
        from .utils import send_discord_webhook

        board_url = request.build_absolute_uri(
            redirect("aa_kanban:board_detail", board_slug=board.slug).url
        )
        msg = _(
            "📋 **New Kanban Board Created:** [{board_name}]({board_url})\n"
            "Created by: `{username}`"
        ).format(
            board_name=board.name,
            board_url=board_url,
            username=request.user.username,
        )
        send_discord_webhook(settings_obj.board_creation_webhook, msg)

    return JsonResponse(
        {
            "board": {
                "id": board.pk,
                "name": board.name,
                "slug": board.slug,
                "description": board.description,
            }
        },
        status=201,
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_edit_board(request: HttpRequest, board_slug: str) -> JsonResponse:
    """Update board metadata, settings, and group permissions."""
    board = get_object_or_404(Board, slug=board_slug)
    data = _json_body(request)

    def _opt_int(val: Any) -> int | None:
        if val is None or val == "":
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    name = str(data.get("name", board.name)).strip()
    if not name:
        return JsonResponse({"error": _("Board name is required.")}, status=400)

    board.name = name[:255]
    if "description" in data:
        board.description = str(data["description"]).strip()
    if "is_ticket_board" in data:
        board.is_ticket_board = bool(data["is_ticket_board"])
    if "is_members_board" in data:
        board.is_members_board = bool(data["is_members_board"])
    if "own_cards_only" in data:
        board.own_cards_only = bool(data["own_cards_only"])
    if "discord_ticket_channel_id" in data:
        board.discord_ticket_channel_id = _opt_int(data["discord_ticket_channel_id"])
    if "discord_alert_channel_id" in data:
        board.discord_alert_channel_id = _opt_int(data["discord_alert_channel_id"])
    if "discord_alert_webhook" in data:
        board.discord_alert_webhook = str(data["discord_alert_webhook"]).strip() or None
    if "discord_webhook_cards" in data:
        board.discord_webhook_cards = str(data["discord_webhook_cards"]).strip() or None
    if "stale_card_alert_hours" in data:
        board.stale_card_alert_hours = max(
            0, _opt_int(data["stale_card_alert_hours"]) or 0
        )
    if "stale_card_repeat_hours" in data:
        board.stale_card_repeat_hours = max(
            0, _opt_int(data["stale_card_repeat_hours"]) or 0
        )
    if "archive_after_days" in data:
        board.archive_after_days = max(0, _opt_int(data["archive_after_days"]) or 0)

    with transaction.atomic():
        board.save()
        if isinstance(data.get("view_group_ids"), list):
            board.view_groups.set(
                KanbanGroup.objects.filter(pk__in=data["view_group_ids"])
            )
        if isinstance(data.get("write_group_ids"), list):
            board.write_groups.set(
                KanbanGroup.objects.filter(pk__in=data["write_group_ids"])
            )

    return JsonResponse({"ok": True, "slug": board.slug})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_archive_board(request: HttpRequest, board_slug: str) -> JsonResponse:
    """Archive a board."""
    board = get_object_or_404(Board, slug=board_slug)
    board.is_archived = True
    board.archived_at = timezone.now()
    board.save(update_fields=["is_archived", "archived_at", "updated_at"])
    return JsonResponse({"ok": True})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_restore_board(request: HttpRequest, board_slug: str) -> JsonResponse:
    """Restore an archived board."""
    board = get_object_or_404(Board, slug=board_slug)
    board.is_archived = False
    board.archived_at = None
    board.save(update_fields=["is_archived", "archived_at", "updated_at"])
    return JsonResponse({"ok": True})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_delete_board(request: HttpRequest, board_slug: str) -> JsonResponse:
    """Delete a board (requires manage_boards or creator)."""
    board = get_object_or_404(Board, slug=board_slug)
    if not (
        user_can_manage_boards(request.user) or board.created_by_id == request.user.pk
    ):
        raise PermissionDenied("You do not have permission to delete this board.")
    board.delete()
    return JsonResponse({"ok": True})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_GET
def api_archived_boards(request: HttpRequest) -> JsonResponse:
    """Return all archived boards."""
    boards = (
        Board.objects.filter(is_archived=True)
        .select_related("created_by")
        .annotate(card_count=Count("lists__cards", distinct=True))
        .order_by("-archived_at", "name")
    )
    return JsonResponse(
        {
            "boards": [
                {
                    "id": b.pk,
                    "name": b.name,
                    "slug": b.slug,
                    "description": b.description,
                    "card_count": b.card_count,
                    "archived_at": (
                        b.archived_at.isoformat() if b.archived_at else None
                    ),
                    "created_by": _serialize_user(b.created_by),
                }
                for b in boards
            ]
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_edit_list(request: HttpRequest, list_id: int) -> JsonResponse:
    """Edit a column's name, description, or WIP limit."""
    lst = get_object_or_404(List.objects.select_related("board"), pk=list_id)
    if not lst.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required.")
    data = _json_body(request)
    name = str(data.get("name", lst.name)).strip()
    if not name:
        return JsonResponse({"error": _("Column name is required.")}, status=400)
    lst.name = name[:100]
    if "description" in data:
        lst.description = str(data["description"]).strip()
    if "wip_limit" in data:
        try:
            lst.wip_limit = max(0, int(data["wip_limit"]))
        except (ValueError, TypeError):
            pass
    lst.save(update_fields=["name", "description", "wip_limit", "updated_at"])
    return JsonResponse(
        {
            "list": {
                "id": lst.pk,
                "name": lst.name,
                "description": lst.description,
                "wip_limit": lst.wip_limit,
                "order": lst.order,
                "can_add_card": True,
            }
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_delete_list(request: HttpRequest, list_id: int) -> JsonResponse:
    """Delete a column."""
    lst = get_object_or_404(List.objects.select_related("board"), pk=list_id)
    if not lst.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required.")
    lst.delete()
    return JsonResponse({"ok": True})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_GET
def api_archived_cards(request: HttpRequest, board_slug: str) -> JsonResponse:
    """Return archived cards for a board."""
    board = get_object_or_404(Board, slug=board_slug)
    if not board.can_user_view(request.user):
        raise PermissionDenied("You do not have permission to view this board.")
    cards = (
        board.visible_cards(
            Card.objects.filter(list__board=board, is_archived=True),
            request.user,
        )
        .select_related("list", "created_by", "assigned_team")
        .prefetch_related("labels", "assignees")
        .order_by("-archived_at")
    )
    return JsonResponse(
        {
            "board_name": board.name,
            "board_slug": board.slug,
            "can_write": board.can_user_write(request.user),
            "cards": [
                {
                    **_serialize_card(c),
                    "list_name": c.list.name,
                    "archived_at": (
                        c.archived_at.isoformat() if c.archived_at else None
                    ),
                }
                for c in cards
            ],
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_POST
def api_restore_card(request: HttpRequest, card_id: int) -> JsonResponse:
    """Restore an archived card back onto its board."""
    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required.")
    card.is_archived = False
    card.archived_at = None
    card.moved_to_list_at = timezone.now()
    card.save(
        update_fields=[
            "is_archived",
            "archived_at",
            "moved_to_list_at",
            "updated_at",
        ]
    )
    return JsonResponse({"ok": True})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_GET
def api_summary(request: HttpRequest) -> JsonResponse:
    """Return cross-board summary of active management boards and their cards."""
    boards = list(
        Board.objects.visible_to(request.user)
        .active()
        .filter(is_members_board=False)
        .order_by("name")
    )
    own_only_ids = [b.pk for b in boards if not b.can_user_see_all_cards(request.user)]
    cards_qs = Card.objects.filter(is_archived=False)
    if own_only_ids:
        cards_qs = cards_qs.exclude(
            Q(list__board_id__in=own_only_ids)
            & ~Q(pk__in=Card.objects.owned_by(request.user).values("pk"))
        )
    prefetch_related_objects(
        boards,
        Prefetch(
            "lists",
            queryset=List.objects.order_by("order", "id").prefetch_related(
                Prefetch(
                    "cards",
                    queryset=cards_qs.select_related(
                        "created_by", "assigned_team"
                    ).prefetch_related("assignees", "labels"),
                )
            ),
        ),
    )
    result = []
    for board in boards:
        lists_out = []
        total_cards = 0
        for lst in board.lists.all():
            c_list = list(lst.cards.all())
            total_cards += len(c_list)
            lists_out.append(
                {
                    "id": lst.pk,
                    "name": lst.name,
                    "wip_limit": lst.wip_limit,
                    "cards": [
                        {
                            "id": c.pk,
                            "title": c.title,
                            "due_date": (
                                c.due_date.isoformat() if c.due_date else None
                            ),
                            "labels": [_serialize_label(lbl) for lbl in c.labels.all()],
                            "assignees": [
                                _serialize_user(u) for u in c.assignees.all()
                            ],
                        }
                        for c in c_list
                    ],
                }
            )
        result.append(
            {
                "id": board.pk,
                "name": board.name,
                "slug": board.slug,
                "total_cards": total_cards,
                "lists": lists_out,
            }
        )
    return JsonResponse({"boards": result})


@login_required
@permission_required("aa_kanban.create_ticket", raise_exception=True)
@require_GET
def api_ticket_options(request: HttpRequest) -> JsonResponse:
    """Return teams and labels available for ticket submission."""
    teams = KanbanTeam.objects.filter(
        ticket_board__is_ticket_board=True, ticket_board__is_archived=False
    ).order_by("name")
    labels = Label.objects.filter(is_ticket_label=True).order_by("name")
    return JsonResponse(
        {
            "teams": [
                {
                    "id": t.pk,
                    "name": t.name,
                    "board_name": t.ticket_board.name if t.ticket_board else "",
                }
                for t in teams
            ],
            "labels": [_serialize_label(lbl) for lbl in labels],
        }
    )


@login_required
@permission_required("aa_kanban.create_ticket", raise_exception=True)
@require_POST
def api_create_ticket(request: HttpRequest) -> JsonResponse:
    """Create a ticket card on the selected team's ticket board."""
    data = _json_body(request)
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    team_id = data.get("assigned_team_id")
    label_id = data.get("label_id")

    if not title:
        return JsonResponse({"error": _("Title is required.")}, status=400)
    try:
        team = KanbanTeam.objects.select_related("ticket_board").get(pk=team_id)
    except (KanbanTeam.DoesNotExist, ValueError, TypeError):
        return JsonResponse({"error": _("Invalid team selected.")}, status=400)

    board = team.ticket_board
    if not board or not board.is_ticket_board or board.is_archived:
        return JsonResponse(
            {
                "error": _(
                    "The selected team does not have a valid ticket board configured."
                )
            },
            status=400,
        )

    list_obj = (
        board.lists.filter(name__iexact="Backlog").first()
        or board.lists.order_by("order", "id").first()
    )
    if not list_obj:
        return JsonResponse(
            {"error": _("No columns available on the ticket board.")}, status=400
        )

    card = Card.objects.create(
        list=list_obj,
        title=title[:255],
        description=description,
        created_by=request.user,
        assigned_team=team,
        moved_to_list_at=timezone.now(),
    )
    if label_id:
        try:
            card.labels.add(Label.objects.get(pk=label_id))
        except (Label.DoesNotExist, ValueError, TypeError):
            pass

    if board.discord_webhook_cards:
        from .utils import send_discord_webhook

        url = request.build_absolute_uri(
            redirect("aa_kanban:board_detail", board_slug=board.slug).url
        )
        msg = _(
            "**New Ticket Submitted!**\nTitle: `{card_title}`\n"
            "Created by: `{username}`\n[View Board]({url})"
        ).format(card_title=card.title, username=request.user.username, url=url)
        send_discord_webhook(board.discord_webhook_cards, msg)

    from .tasks import create_ticket_thread

    create_ticket_thread.delay(card.pk)

    return JsonResponse(
        {
            "ok": True,
            "card_id": card.pk,
            "board_slug": board.slug,
            "board_name": board.name,
        },
        status=201,
    )


def _serialize_settings_payload() -> dict[str, Any]:
    """Serialize full settings state for Groups, Teams, Labels, and Global Config."""
    groups = KanbanGroup.objects.prefetch_related("members", "groups").order_by("name")
    teams = (
        KanbanTeam.objects.select_related("ticket_board")
        .prefetch_related("members", "groups")
        .order_by("name")
    )
    labels = Label.objects.order_by("name")
    cfg = KanbanSetting.get_settings()
    boards = Board.objects.active().order_by("name")
    return {
        "groups": [
            {
                "id": g.pk,
                "name": g.name,
                "can_manage_boards": g.can_manage_boards,
                "members": [
                    {"id": u.pk, "username": u.username} for u in g.members.all()
                ],
                "auth_groups": [
                    {"id": ag.pk, "name": ag.name} for ag in g.groups.all()
                ],
            }
            for g in groups
        ],
        "teams": [
            {
                "id": t.pk,
                "name": t.name,
                "discord_role_id": (
                    str(t.discord_role_id) if t.discord_role_id else ""
                ),
                "ticket_board_id": t.ticket_board_id,
                "ticket_board_name": t.ticket_board.name if t.ticket_board else "",
                "members": [
                    {"id": u.pk, "username": u.username} for u in t.members.all()
                ],
                "auth_groups": [
                    {"id": ag.pk, "name": ag.name} for ag in t.groups.all()
                ],
            }
            for t in teams
        ],
        "labels": [_serialize_label(lbl) for lbl in labels],
        "global_settings": {
            "board_creation_webhook": cfg.board_creation_webhook or "",
            "members_page_name": cfg.members_page_name,
        },
        "boards": [
            {
                "id": b.pk,
                "name": b.name,
                "is_ticket_board": b.is_ticket_board,
            }
            for b in boards
        ],
        "all_users": [
            {"id": u.pk, "username": u.username}
            for u in User.objects.filter(is_active=True).order_by("username")[:300]
        ],
        "all_auth_groups": [
            {"id": ag.pk, "name": ag.name} for ag in AuthGroup.objects.order_by("name")
        ],
    }


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_GET
def api_settings(request: HttpRequest) -> JsonResponse:
    """Return full Kanban settings payload."""
    return JsonResponse(_serialize_settings_payload())


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_update_global_settings(request: HttpRequest) -> JsonResponse:
    """Update global Kanban settings."""
    data = _json_body(request)
    cfg = KanbanSetting.get_settings()
    cfg.board_creation_webhook = (
        str(data.get("board_creation_webhook", "")).strip() or None
    )
    members_name = str(data.get("members_page_name", "")).strip()
    if members_name:
        cfg.members_page_name = members_name[:50]
    cfg.save()
    return JsonResponse(_serialize_settings_payload())


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_save_group(request: HttpRequest) -> JsonResponse:
    """Create or update a KanbanGroup and its members/auth_groups."""
    data = _json_body(request)
    name = str(data.get("name", "")).strip()
    if not name:
        return JsonResponse({"error": _("Group name is required.")}, status=400)
    group_id = data.get("id")
    with transaction.atomic():
        if group_id:
            group = get_object_or_404(KanbanGroup, pk=group_id)
            group.name = name[:255]
            group.can_manage_boards = bool(data.get("can_manage_boards", False))
            group.save()
        else:
            group = KanbanGroup.objects.create(
                name=name[:255],
                can_manage_boards=bool(data.get("can_manage_boards", False)),
            )
        if isinstance(data.get("member_ids"), list):
            group.members.set(User.objects.filter(pk__in=data["member_ids"]))
        if isinstance(data.get("auth_group_ids"), list):
            group.groups.set(AuthGroup.objects.filter(pk__in=data["auth_group_ids"]))
    return JsonResponse(_serialize_settings_payload())


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_delete_group(request: HttpRequest, group_id: int) -> JsonResponse:
    """Delete a KanbanGroup."""
    get_object_or_404(KanbanGroup, pk=group_id).delete()
    return JsonResponse(_serialize_settings_payload())


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_save_team(request: HttpRequest) -> JsonResponse:
    """Create or update a KanbanTeam and its members/auth_groups."""
    data = _json_body(request)
    name = str(data.get("name", "")).strip()
    if not name:
        return JsonResponse({"error": _("Team name is required.")}, status=400)
    raw_role = str(data.get("discord_role_id", "") or "").strip()
    discord_role_id = int(raw_role) if raw_role.isdigit() else None
    raw_board = data.get("ticket_board_id")
    ticket_board = (
        Board.objects.filter(pk=raw_board).first()
        if raw_board not in (None, "")
        else None
    )
    team_id = data.get("id")
    with transaction.atomic():
        if team_id:
            team = get_object_or_404(KanbanTeam, pk=team_id)
            team.name = name[:255]
            team.discord_role_id = discord_role_id
            team.ticket_board = ticket_board
            team.save()
        else:
            team = KanbanTeam.objects.create(
                name=name[:255],
                discord_role_id=discord_role_id,
                ticket_board=ticket_board,
            )
        if isinstance(data.get("member_ids"), list):
            team.members.set(User.objects.filter(pk__in=data["member_ids"]))
        if isinstance(data.get("auth_group_ids"), list):
            team.groups.set(AuthGroup.objects.filter(pk__in=data["auth_group_ids"]))
    return JsonResponse(_serialize_settings_payload())


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_delete_team(request: HttpRequest, team_id: int) -> JsonResponse:
    """Delete a KanbanTeam."""
    get_object_or_404(KanbanTeam, pk=team_id).delete()
    return JsonResponse(_serialize_settings_payload())


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_save_label(request: HttpRequest) -> JsonResponse:
    """Create or update a global Label."""
    data = _json_body(request)
    name = str(data.get("name", "")).strip()
    if not name:
        return JsonResponse({"error": _("Label name is required.")}, status=400)
    color = str(data.get("color", "primary")).strip() or "primary"
    is_ticket_label = bool(data.get("is_ticket_label", False))
    label_id = data.get("id")
    if label_id:
        lbl = get_object_or_404(Label, pk=label_id)
        lbl.name = name[:50]
        lbl.color = color[:20]
        lbl.is_ticket_label = is_ticket_label
        lbl.save()
    else:
        Label.objects.create(
            name=name[:50], color=color[:20], is_ticket_label=is_ticket_label
        )
    return JsonResponse(_serialize_settings_payload())


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@manage_boards_required
@require_POST
def api_delete_label(request: HttpRequest, label_id: int) -> JsonResponse:
    """Delete a global Label."""
    get_object_or_404(Label, pk=label_id).delete()
    return JsonResponse(_serialize_settings_payload())


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@require_GET
def spa_app(request: HttpRequest, subpath: str = "") -> HttpResponse:
    """Host template for the React + shadcn/ui SPA."""
    from django.conf import settings

    app_name = getattr(settings, "AA_KANBAN_APP_NAME", "Kanban")
    context = {
        "title": app_name,
        "app_name": app_name,
    }
    return render(request, "aa_kanban/spa.html", context)
