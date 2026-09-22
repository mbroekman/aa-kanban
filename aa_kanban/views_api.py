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

from .models import Board, Card, Comment, List, Label


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

    source_list = card.list

    if source_list.id != target_list.id and target_list.wip_limit > 0:
        if target_list.cards.count() >= target_list.wip_limit:
            return HttpResponseBadRequest("Target list has reached its WIP limit.")

    with transaction.atomic():
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
                    
    if source_list.id != target_list.id and board.discord_webhook_cards:
        from aa_kanban.utils import send_discord_webhook
        msg = f"Card moved: **{card.title}** was moved from `{source_list.name}` to `{target_list.name}`."
        send_discord_webhook(board.discord_webhook_cards, msg)

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
    available_labels = []
    if can_write:
        available_users = list(
            User.objects.filter(is_active=True)
            .exclude(pk__in=card.assignees.values_list("pk", flat=True))
            .order_by("username")[:20]
        )
        available_labels = list(
            board.labels.exclude(pk__in=card.labels.values_list("pk", flat=True))
            .order_by("name")
        )

    context = {
        "card": card,
        "can_write": can_write,
        "available_users": available_users,
        "available_labels": available_labels,
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
        try:
            from aadiscordbot.tasks import send_direct_message_by_user_id
            msg = f"You have been removed from the card: **{card.title}** on board **{board.name}**."
            send_direct_message_by_user_id.delay(target_user.pk, msg)
        except ImportError:
            pass
    else:
        card.assignees.add(target_user)
        try:
            from aadiscordbot.tasks import send_direct_message_by_user_id
            msg = f"You have been assigned to the card: **{card.title}** on board **{board.name}**."
            send_direct_message_by_user_id.delay(target_user.pk, msg)
        except ImportError:
            pass

    available_users = list(
        User.objects.filter(is_active=True)
        .exclude(pk__in=card.assignees.values_list("pk", flat=True))
        .order_by("username")[:20]
    )

    from django.template.loader import render_to_string
    html_partial = render_to_string(
        "aa_kanban/partials/card_assignees.html",
        {
            "card": card,
            "can_write": True,
            "available_users": available_users,
        },
        request=request,
    )
    oob_partial = render_to_string(
        "aa_kanban/partials/card_item.html",
        {"card": card, "hx_oob": True, "can_write": True},
        request=request,
    )
    return HttpResponse(html_partial + oob_partial)


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
def edit_list(request: HttpRequest, list_id: int) -> HttpResponse:
    """Edit a list (column) settings and return the updated column header partial."""
    kanban_list = get_object_or_404(
        List.objects.select_related("board"), pk=list_id
    )
    if not kanban_list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to edit a column.")

    if request.method == "GET":
        return render(
            request,
            "aa_kanban/partials/edit_list_modal.html",
            {"list": kanban_list},
        )

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        try:
            wip_limit = int(request.POST.get("wip_limit", 0))
            if wip_limit < 0:
                wip_limit = 0
        except ValueError:
            wip_limit = 0

        if not name:
            return HttpResponseBadRequest("Column name cannot be empty.")

        kanban_list.name = name
        kanban_list.description = description
        kanban_list.wip_limit = wip_limit
        kanban_list.save(update_fields=["name", "description", "wip_limit", "updated_at"])

        response = render(
            request,
            "aa_kanban/partials/column_header.html",
            {"list": kanban_list, "can_write": True},
        )
        response["HX-Trigger"] = "closeModal"
        return response

    return HttpResponseNotAllowed(["GET", "POST"])


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

@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def board_labels_modal(request: HttpRequest, board_slug: str) -> HttpResponse:
    """Render the modal dialog body for managing board labels."""
    board = get_object_or_404(Board, slug=board_slug)
    
    can_manage = request.user.has_perm("aa_kanban.manage_boards")
    can_write = board.can_user_write(request.user)
    
    if not (can_manage or can_write):
        raise PermissionDenied("You do not have permission to manage labels for this board.")
        
    context = {
        "board": board,
        "labels": board.labels.order_by("name"),
    }
    return render(request, "aa_kanban/partials/board_labels_modal.html", context)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def create_label(request: HttpRequest, board_slug: str) -> HttpResponse:
    """Create a new label for a board."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    board = get_object_or_404(Board, slug=board_slug)
    
    can_manage = request.user.has_perm("aa_kanban.manage_boards")
    can_write = board.can_user_write(request.user)
    
    if not (can_manage or can_write):
        raise PermissionDenied("You do not have permission to manage labels for this board.")

    name = request.POST.get("name", "").strip()
    color = request.POST.get("color", "primary").strip()
    
    if not name:
        return HttpResponseBadRequest("Label name cannot be empty.")
        
    Label.objects.get_or_create(board=board, name=name, defaults={"color": color})
    
    context = {
        "board": board,
        "labels": board.labels.order_by("name"),
    }
    return render(request, "aa_kanban/partials/board_labels_modal.html", context)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def delete_label(request: HttpRequest, label_id: int) -> HttpResponse:
    """Delete a label from a board."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    label = get_object_or_404(Label.objects.select_related("board"), pk=label_id)
    board = label.board
    
    can_manage = request.user.has_perm("aa_kanban.manage_boards")
    can_write = board.can_user_write(request.user)
    
    if not (can_manage or can_write):
        raise PermissionDenied("You do not have permission to delete labels for this board.")

    label.delete()
    
    context = {
        "board": board,
        "labels": board.labels.order_by("name"),
    }
    return render(request, "aa_kanban/partials/board_labels_modal.html", context)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def toggle_label(request: HttpRequest, card_id: int) -> HttpResponse:
    """Add or remove a label from a card and return updated labels partial."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(
        Card.objects.select_related("list__board").prefetch_related("labels"),
        pk=card_id,
    )
    board = card.list.board
    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to assign labels.")

    label_id_raw = request.POST.get("label_id")
    if not label_id_raw:
        return HttpResponseBadRequest("Missing label_id.")

    try:
        label_id = int(label_id_raw)
    except (ValueError, TypeError):
        return HttpResponseBadRequest("label_id must be an integer.")

    target_label = get_object_or_404(Label, pk=label_id, board=board)

    if card.labels.filter(pk=target_label.pk).exists():
        card.labels.remove(target_label)
    else:
        card.labels.add(target_label)

    available_labels = list(
        board.labels.exclude(pk__in=card.labels.values_list("pk", flat=True))
        .order_by("name")
    )

    from django.template.loader import render_to_string
    html_partial = render_to_string(
        "aa_kanban/partials/card_labels.html",
        {
            "card": card,
            "can_write": True,
            "available_labels": available_labels,
        },
        request=request,
    )
    oob_partial = render_to_string(
        "aa_kanban/partials/card_item.html",
        {"card": card, "hx_oob": True, "can_write": True},
        request=request,
    )
    return HttpResponse(html_partial + oob_partial)
