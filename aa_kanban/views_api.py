"""API and AJAX views for aa_kanban."""

import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render

from .models import Board, Card, Comment, List


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def move_card(request: HttpRequest, card_id: int) -> HttpResponse:
    """Move a card to a target list and new position within the same board."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(
        Card.objects.select_related("list__board"), pk=card_id
    )
    board = card.list.board

    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required for this board.")

    if request.content_type == "application/json":
        try:
            body_data = json.loads(request.body)
            target_list_id_raw = body_data.get("target_list_id")
            new_position_raw = body_data.get("new_position")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HttpResponseBadRequest("Invalid JSON body.")
    else:
        target_list_id_raw = request.POST.get("target_list_id")
        new_position_raw = request.POST.get("new_position")

    if target_list_id_raw is None or new_position_raw is None:
        return HttpResponseBadRequest("Missing target_list_id or new_position.")

    try:
        target_list_id = int(target_list_id_raw)
        new_position = int(new_position_raw)
    except (ValueError, TypeError):
        return HttpResponseBadRequest(
            "target_list_id and new_position must be integers."
        )

    target_list = get_object_or_404(List, pk=target_list_id)

    # Validate that both lists belong to the exact same board
    if target_list.board_id != board.id:
        return HttpResponseBadRequest(
            "Target list does not belong to the same board."
        )

    with transaction.atomic():
        source_list = card.list
        target_cards = list(
            target_list.cards.exclude(pk=card.pk).order_by("order", "id")
        )
        clamped_pos = max(0, min(new_position, len(target_cards)))
        target_cards.insert(clamped_pos, card)

        for idx, c in enumerate(target_cards):
            if c.pk == card.pk:
                c.list = target_list
                c.order = idx
                c.save(update_fields=["list", "order", "updated_at"])
            elif c.order != idx:
                c.order = idx
                c.save(update_fields=["order"])

        if source_list.id != target_list.id:
            source_cards = list(
                source_list.cards.exclude(pk=card.pk).order_by("order", "id")
            )
            for idx, c in enumerate(source_cards):
                if c.order != idx:
                    c.order = idx
                    c.save(update_fields=["order"])

    return JsonResponse(
        {
            "status": "success",
            "card_id": card.id,
            "target_list_id": target_list.id,
            "new_position": card.order,
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def card_modal(request: HttpRequest, card_id: int) -> HttpResponse:
    """Render the modal dialog body for a card."""
    card = get_object_or_404(
        Card.objects.select_related(
            "list__board", "created_by"
        ).prefetch_related("labels", "assignees", "comments__author"),
        pk=card_id,
    )
    board = card.list.board
    if not board.can_user_view(request.user):
        raise PermissionDenied("You do not have permission to view this card.")

    can_write = board.can_user_write(request.user)

    available_users = []
    if can_write:
        available_users = list(
            User.objects.filter(is_active=True)
            .exclude(pk__in=card.assignees.values_list("pk", flat=True))
            .order_by("username")[:20]
        )

    context = {
        "card": card,
        "can_write": can_write,
        "available_users": available_users,
    }
    return render(
        request, "aa_kanban/partials/card_modal_content.html", context
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def add_comment(request: HttpRequest, card_id: int) -> HttpResponse:
    """Add a new comment to a card and return updated comments partial."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(
        Card.objects.select_related("list__board"), pk=card_id
    )
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to comment.")

    comment_text = request.POST.get("comment", "").strip()
    if not comment_text:
        return HttpResponseBadRequest("Comment text cannot be empty.")

    Comment.objects.create(
        card=card, author=request.user, text=comment_text  # type: ignore[misc]
    )

    comments = card.comments.select_related("author").order_by("created_at")
    return render(
        request,
        "aa_kanban/partials/card_comments.html",
        {"comments": comments},
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def toggle_assignee(request: HttpRequest, card_id: int) -> HttpResponse:
    """Add or remove an assignee from a card and return updated assignees partial."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(
        Card.objects.select_related("list__board").prefetch_related(
            "assignees"
        ),
        pk=card_id,
    )
    board = card.list.board
    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to assign users.")

    user_id_raw = request.POST.get("user_id")
    if not user_id_raw:
        return HttpResponseBadRequest("Missing user_id.")

    try:
        user_id = int(user_id_raw)
    except (ValueError, TypeError):
        return HttpResponseBadRequest("user_id must be an integer.")

    target_user = get_object_or_404(User, pk=user_id)

    if card.assignees.filter(pk=target_user.pk).exists():
        card.assignees.remove(target_user)
    else:
        card.assignees.add(target_user)

    available_users = list(
        User.objects.filter(is_active=True)
        .exclude(pk__in=card.assignees.values_list("pk", flat=True))
        .order_by("username")[:20]
    )

    return render(
        request,
        "aa_kanban/partials/card_assignees.html",
        {
            "card": card,
            "can_write": True,
            "available_users": available_users,
        },
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def update_card(request: HttpRequest, card_id: int) -> HttpResponse:
    """Update card description or title."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(
        Card.objects.select_related("list__board"), pk=card_id
    )
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to update card.")

    if "description" in request.POST:
        card.description = request.POST.get("description", "").strip()
        card.save(update_fields=["description", "updated_at"])

    if "title" in request.POST:
        new_title = request.POST.get("title", "").strip()
        if new_title:
            card.title = new_title
            card.save(update_fields=["title", "updated_at"])

    return HttpResponse(
        '<span class="text-success"><i class="fas fa-check me-1"></i>Saved!</span>'
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def create_list(request: HttpRequest, board_slug: str) -> HttpResponse:
    """Create a new list (column) in the board and return the column partial."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    board = get_object_or_404(Board, slug=board_slug)
    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to add a column.")

    name = request.POST.get("name", "").strip()
    if not name:
        return HttpResponseBadRequest("Column name cannot be empty.")

    last_order = board.lists.order_by("-order").values_list("order", flat=True).first()
    order = (last_order or 0) + 1
    kanban_list = List.objects.create(board=board, name=name, order=order)

    return render(
        request,
        "aa_kanban/partials/board_column.html",
        {"list": kanban_list, "can_write": True},
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def rename_list(request: HttpRequest, list_id: int) -> HttpResponse:
    """Rename a list (column) and return the updated column header partial."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    kanban_list = get_object_or_404(
        List.objects.select_related("board"), pk=list_id
    )
    if not kanban_list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to rename a column.")

    name = request.POST.get("name", "").strip()
    if not name:
        return HttpResponseBadRequest("Column name cannot be empty.")

    kanban_list.name = name
    kanban_list.save(update_fields=["name", "updated_at"])

    return render(
        request,
        "aa_kanban/partials/column_header.html",
        {"list": kanban_list, "can_write": True},
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def delete_list(request: HttpRequest, list_id: int) -> HttpResponse:
    """Delete a list (column) and all its cards. Returns empty 200."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    kanban_list = get_object_or_404(
        List.objects.select_related("board"), pk=list_id
    )
    if not kanban_list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to delete a column.")

    kanban_list.delete()
    return HttpResponse(status=200)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def create_card(request: HttpRequest, list_id: int) -> HttpResponse:
    """Create a new card in a list and return the card partial."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    kanban_list = get_object_or_404(
        List.objects.select_related("board"), pk=list_id
    )
    if not kanban_list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to add a card.")

    title = request.POST.get("title", "").strip()
    if not title:
        return HttpResponseBadRequest("Card title cannot be empty.")

    last_order = (
        kanban_list.cards.order_by("-order").values_list("order", flat=True).first()
    )
    order = (last_order or 0) + 1
    card = Card.objects.create(
        list=kanban_list,
        title=title,
        order=order,
        created_by=request.user,  # type: ignore[misc]
    )

    return render(
        request,
        "aa_kanban/partials/card_item.html",
        {"card": card, "can_write": True},
    )
