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
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Board, Card, Comment, Label, List


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def move_card(request: HttpRequest, card_id: int) -> HttpResponse:
    """Move a card to a target list and new position within the same board."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    board = card.list.board

    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required for this board.")

    if request.content_type == "application/json":
        try:
            body_data = json.loads(request.body)
            target_list_id_raw = body_data.get("target_list_id")
            new_position_raw = body_data.get("new_position")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HttpResponseBadRequest(_("Invalid JSON body."))
    else:
        target_list_id_raw = request.POST.get("target_list_id")
        new_position_raw = request.POST.get("new_position")

    if target_list_id_raw is None or new_position_raw is None:
        return HttpResponseBadRequest(_("Missing target_list_id or new_position."))

    try:
        target_list_id = int(target_list_id_raw)
        new_position = int(new_position_raw)
    except (ValueError, TypeError):
        return HttpResponseBadRequest(
            _("target_list_id and new_position must be integers.")
        )

    target_list = get_object_or_404(List, pk=target_list_id)

    # Validate that both lists belong to the exact same board
    if target_list.board_id != board.id:
        return HttpResponseBadRequest(
            _("Target list does not belong to the same board.")
        )

    source_list = card.list

    if source_list.id != target_list.id and target_list.wip_limit > 0:
        if target_list.cards.count() >= target_list.wip_limit:
            return HttpResponseBadRequest(_("Target list has reached its WIP limit."))

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
                update_fields = ["list", "order", "updated_at"]
                if source_list.id != target_list.id:
                    c.moved_to_list_at = timezone.now()
                    update_fields.append("moved_to_list_at")
                c.save(update_fields=update_fields)
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

    prompt_close_thread = False
    if source_list.id != target_list.id:
        if card.discord_thread_id:
            from aa_kanban.tasks import notify_ticket_thread

            thread_msg = _(
                "🔄 **Status Update:** Card moved from `{source_list_name}` to `{target_list_name}` by **{username}**."
            ).format(
                source_list_name=source_list.name,
                target_list_name=target_list.name,
                username=request.user.username,
            )
            notify_ticket_thread.delay(card.discord_thread_id, str(thread_msg))

            last_list = board.lists.order_by("order", "id").last()
            if last_list and target_list.id == last_list.id:
                prompt_close_thread = True

        if board.discord_webhook_cards:
            from django.shortcuts import redirect

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

    return JsonResponse(
        {
            "status": "success",
            "card_id": card.id,
            "target_list_id": target_list.id,
            "new_position": card.order,
            "prompt_close_thread": prompt_close_thread,
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def close_card_thread(request: HttpRequest, card_id: int) -> HttpResponse:
    """Archive and lock a card's Discord thread."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to close this thread.")

    if not card.discord_thread_id:
        return HttpResponseBadRequest(_("This card has no Discord thread."))

    from aa_kanban.tasks import close_ticket_thread

    close_ticket_thread.delay(card.discord_thread_id)

    return JsonResponse({"status": "success", "card_id": card.id})


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def card_modal(request: HttpRequest, card_id: int) -> HttpResponse:
    """Render the modal dialog body for a card."""
    card = get_object_or_404(
        Card.objects.select_related("list__board", "created_by").prefetch_related(
            "labels", "assignees", "comments__author"
        ),
        pk=card_id,
    )
    board = card.list.board
    if not board.can_user_view(request.user):
        raise PermissionDenied("You do not have permission to view this card.")

    can_write = board.can_user_write(request.user)

    available_users = []
    available_labels = []
    available_teams = []
    if can_write:
        available_users = list(
            User.objects.filter(is_active=True)
            .exclude(pk__in=card.assignees.values_list("pk", flat=True))
            .order_by("username")
        )
        available_labels = list(
            Label.objects.exclude(
                pk__in=card.labels.values_list("pk", flat=True)
            ).order_by("name")
        )
        from .models import KanbanTeam

        available_teams = list(KanbanTeam.objects.all())

    context = {
        "card": card,
        "can_write": can_write,
        "available_users": available_users,
        "available_labels": available_labels,
        "available_teams": available_teams,
    }
    return render(request, "aa_kanban/partials/card_modal_content.html", context)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def add_comment(request: HttpRequest, card_id: int) -> HttpResponse:
    """Add a new comment to a card and return updated comments partial."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to comment.")

    comment_text = request.POST.get("comment", "").strip()
    if not comment_text:
        return HttpResponseBadRequest(_("Comment text cannot be empty."))

    Comment.objects.create(
        card=card,
        author=request.user,
        text=comment_text,  # type: ignore[misc]
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
        Card.objects.select_related("list__board").prefetch_related("assignees"),
        pk=card_id,
    )
    board = card.list.board
    if not board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to assign users.")

    user_id_raw = request.POST.get("user_id")
    if not user_id_raw:
        return HttpResponseBadRequest(_("Missing user_id."))

    try:
        user_id = int(user_id_raw)
    except (ValueError, TypeError):
        return HttpResponseBadRequest(_("user_id must be an integer."))

    target_user = get_object_or_404(User, pk=user_id)

    if card.assignees.filter(pk=target_user.pk).exists():
        card.assignees.remove(target_user)
        try:
            from aadiscordbot.tasks import send_direct_message_by_user_id

            msg = _(
                "You have been removed from the card: **{card_title}** on board **{board_name}**."
            ).format(card_title=card.title, board_name=board.name)
            send_direct_message_by_user_id.delay(target_user.pk, str(msg))
        except ImportError:
            pass

        if card.discord_thread_id:
            from aa_kanban.tasks import notify_ticket_thread

            thread_msg = _(
                "👤 **Unassigned:** {target_username} removed by **{username}**."
            ).format(
                target_username=target_user.username, username=request.user.username
            )
            notify_ticket_thread.delay(
                card.discord_thread_id,
                str(thread_msg),
                remove_user_id=target_user.pk,
            )
    else:
        card.assignees.add(target_user)
        try:
            from aadiscordbot.tasks import send_direct_message_by_user_id

            msg = _(
                "You have been assigned to the card: **{card_title}** on board **{board_name}**."
            ).format(card_title=card.title, board_name=board.name)
            send_direct_message_by_user_id.delay(target_user.pk, str(msg))
        except ImportError:
            pass

        if card.discord_thread_id:
            from aa_kanban.tasks import notify_ticket_thread

            thread_msg = _(
                "👤 **Assigned:** {target_username} added by **{username}**."
            ).format(
                target_username=target_user.username, username=request.user.username
            )
            notify_ticket_thread.delay(
                card.discord_thread_id,
                str(thread_msg),
                invite_user_id=target_user.pk,
            )

    available_users = list(
        User.objects.filter(is_active=True)
        .exclude(pk__in=card.assignees.values_list("pk", flat=True))
        .order_by("username")
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

    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to update card.")

    if "description" in request.POST:
        card.description = request.POST.get("description", "").strip()
        card.save(update_fields=["description", "updated_at"])

        from django.template.loader import render_to_string

        status_html = (
            '<span class="text-success"><i class="fas fa-check me-1"></i>Saved!</span>'
        )
        desc_block_html = render_to_string(
            "aa_kanban/partials/card_description_block.html",
            {"card": card, "can_write": True},
            request=request,
        )
        oob_desc_block = (
            '<div id="card-description-block" hx-swap-oob="innerHTML">'
            f"{desc_block_html}</div>"
        )
        return HttpResponse(status_html + oob_desc_block)

    if "title" in request.POST:
        new_title = request.POST.get("title", "").strip()
        if new_title:
            card.title = new_title
            card.save(update_fields=["title", "updated_at"])

        from django.template.loader import render_to_string

        html_partial = render_to_string(
            "aa_kanban/partials/card_title.html",
            {"card": card, "can_write": True},
            request=request,
        )
        oob_partial = render_to_string(
            "aa_kanban/partials/card_item.html",
            {"card": card, "hx_oob": True, "can_write": True},
            request=request,
        )
        return HttpResponse(html_partial + oob_partial)

    return HttpResponseBadRequest(_("No valid fields to update."))


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def update_card_color(request: HttpRequest, card_id: int) -> HttpResponse:
    """Update card background color."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to update card.")

    if "color" in request.POST:
        card.color = request.POST.get("color", "").strip()
        card.save(update_fields=["color"])

    from django.template.loader import render_to_string

    # Reload card to ensure we have all related data for the modal
    card = (
        Card.objects.select_related("list__board")
        .prefetch_related("labels", "assignees", "comments__author")
        .get(pk=card_id)
    )

    html_partial = render_to_string(
        "aa_kanban/partials/card_modal_content.html",
        {"card": card, "can_write": True},
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
def delete_card(request: HttpRequest, card_id: int) -> HttpResponse:
    """Delete a card. Returns empty 200 to remove from DOM."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to delete card.")

    card.delete()

    response = HttpResponse("")
    response["HX-Trigger"] = "closeModal"
    return response


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
        return HttpResponseBadRequest(_("Column name cannot be empty."))

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
    kanban_list = get_object_or_404(List.objects.select_related("board"), pk=list_id)
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
            return HttpResponseBadRequest(_("Column name cannot be empty."))

        kanban_list.name = name
        kanban_list.description = description
        kanban_list.wip_limit = wip_limit
        kanban_list.save(
            update_fields=["name", "description", "wip_limit", "updated_at"]
        )

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

    kanban_list = get_object_or_404(List.objects.select_related("board"), pk=list_id)
    if not kanban_list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to delete a column.")

    kanban_list.delete()
    return HttpResponse(status=200)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def move_list(request: HttpRequest, list_id: int) -> HttpResponse:
    """Move a list/column to a new position within its board."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    kanban_list = get_object_or_404(List.objects.select_related("board"), pk=list_id)
    if not kanban_list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required for this board.")

    if request.content_type == "application/json":
        try:
            body_data = json.loads(request.body)
            new_position_raw = body_data.get("new_position")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HttpResponseBadRequest(_("Invalid JSON body."))
    else:
        new_position_raw = request.POST.get("new_position")

    if new_position_raw is None:
        return HttpResponseBadRequest(_("Missing new_position."))

    try:
        new_position = int(new_position_raw)
    except (ValueError, TypeError):
        return HttpResponseBadRequest(_("new_position must be an integer."))

    from .services import reorder_kanban_list

    updated_list = reorder_kanban_list(
        list_id=kanban_list.id, new_position=new_position
    )

    return JsonResponse(
        {
            "status": "ok",
            "list_id": updated_list.id,
            "new_position": updated_list.order,
        }
    )


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def create_card(request: HttpRequest, list_id: int) -> HttpResponse:
    """Create a new card in a list and return the card partial."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    kanban_list = get_object_or_404(List.objects.select_related("board"), pk=list_id)
    if not kanban_list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to add a card.")

    title = request.POST.get("title", "").strip()
    if not title:
        return HttpResponseBadRequest(_("Card title cannot be empty."))

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

    if kanban_list.board.discord_webhook_cards:
        from django.shortcuts import redirect

        from aa_kanban.utils import send_discord_webhook

        url = request.build_absolute_uri(
            redirect("aa_kanban:board_detail", board_slug=kanban_list.board.slug).url
        )
        msg = _(
            "**New Card Created!**\n"
            "Title: `{card_title}`\n"
            "Created by: `{username}`\n"
            "List: `{list_name}`\n"
            "[View Board]({url})"
        ).format(
            card_title=card.title,
            username=request.user.username,
            list_name=kanban_list.name,
            url=url,
        )
        send_discord_webhook(kanban_list.board.discord_webhook_cards, msg)

    return render(
        request,
        "aa_kanban/partials/card_item.html",
        {"card": card, "can_write": True, "auto_open": True},
    )


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
        return HttpResponseBadRequest(_("Missing label_id."))

    try:
        label_id = int(label_id_raw)
    except (ValueError, TypeError):
        return HttpResponseBadRequest(_("label_id must be an integer."))

    target_label = get_object_or_404(Label, pk=label_id)

    if card.labels.filter(pk=target_label.pk).exists():
        card.labels.remove(target_label)
        is_added = False
    else:
        card.labels.add(target_label)
        is_added = True

    if card.discord_thread_id:
        from aa_kanban.tasks import notify_ticket_thread

        if is_added:
            label_msg = _(
                "🏷️ **Label Added:** `{label_name}` by **{username}**."
            ).format(
                label_name=target_label.name,
                username=request.user.username,
            )
        else:
            label_msg = _(
                "🏷️ **Label Removed:** `{label_name}` by **{username}**."
            ).format(
                label_name=target_label.name,
                username=request.user.username,
            )
        notify_ticket_thread.delay(card.discord_thread_id, str(label_msg))

    available_labels = list(
        Label.objects.exclude(pk__in=card.labels.values_list("pk", flat=True)).order_by(
            "name"
        )
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


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def update_card_team(request: HttpRequest, card_id: int) -> HttpResponse:
    """Update assigned team on a card."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(Card.objects.select_related("list__board"), pk=card_id)
    if not card.list.board.can_user_write(request.user):
        raise PermissionDenied("Write permission required to update card.")

    team_id = request.POST.get("team_id")
    if team_id:
        from .models import KanbanTeam

        card.assigned_team = KanbanTeam.objects.filter(pk=team_id).first()
    else:
        card.assigned_team = None
    card.save(update_fields=["assigned_team", "updated_at"])

    if card.discord_thread_id:
        from aa_kanban.tasks import notify_ticket_thread

        if card.assigned_team:
            team_role_mention = ""
            if card.assigned_team.discord_role_id:
                team_role_mention = f" <@&{card.assigned_team.discord_role_id}>"
            team_msg = _(
                "👥 **Team Update:** Assigned to **{team_name}**{role_mention} by **{username}**."
            ).format(
                team_name=card.assigned_team.name,
                role_mention=team_role_mention,
                username=request.user.username,
            )
            notify_ticket_thread.delay(
                card.discord_thread_id,
                str(team_msg),
                team_id=card.assigned_team.id,
            )
        else:
            team_msg = _(
                "👥 **Team Update:** Team unassigned by **{username}**."
            ).format(username=request.user.username)
            notify_ticket_thread.delay(card.discord_thread_id, str(team_msg))

    from django.template.loader import render_to_string

    from .models import KanbanTeam

    html_partial = render_to_string(
        "aa_kanban/partials/card_team.html",
        {
            "card": card,
            "can_write": True,
            "available_teams": KanbanTeam.objects.all(),
        },
        request=request,
    )
    oob_partial = render_to_string(
        "aa_kanban/partials/card_item.html",
        {"card": card, "hx_oob": True, "can_write": True},
        request=request,
    )
    return HttpResponse(html_partial + oob_partial)


MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _detect_image_type(chunk: bytes) -> str | None:
    """Detect image type from initial bytes."""
    if chunk.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if chunk.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if chunk.startswith(b"GIF87a") or chunk.startswith(b"GIF89a"):
        return "gif"
    if chunk.startswith(b"RIFF") and len(chunk) >= 12 and chunk[8:12] == b"WEBP":
        return "webp"
    return None


@login_required
def upload_image(request: HttpRequest) -> JsonResponse:
    """Upload an image file for use in card descriptions or ticket forms."""
    if not (
        request.user.has_perm("aa_kanban.basic_access")
        or request.user.has_perm("aa_kanban.create_ticket")
    ):
        raise PermissionDenied("Permission required to upload images.")

    if request.method != "POST":
        return JsonResponse({"error": str(_("Method not allowed."))}, status=405)

    upload_file = request.FILES.get("image") or request.FILES.get("file")
    if not upload_file:
        return JsonResponse({"error": str(_("No image file provided."))}, status=400)

    if upload_file.size > MAX_UPLOAD_SIZE:
        return JsonResponse(
            {"error": str(_("Image exceeds maximum size limit of 5MB."))},
            status=400,
        )

    import os

    ext = os.path.splitext(upload_file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return JsonResponse(
            {
                "error": str(
                    _("Unsupported image format. Allowed formats: PNG, JPG, GIF, WebP.")
                )
            },
            status=400,
        )

    # Validate image magic bytes
    initial_bytes = upload_file.read(16)
    upload_file.seek(0)
    detected_type = _detect_image_type(initial_bytes)
    if not detected_type:
        return JsonResponse(
            {"error": str(_("Invalid or corrupted image file."))},
            status=400,
        )

    from .models import KanbanAttachment

    attachment = KanbanAttachment.objects.create(
        uploader=request.user,
        file=upload_file,
        original_filename=upload_file.name,
        size=upload_file.size,
    )

    file_url = attachment.file.url
    return JsonResponse(
        {
            "id": attachment.id,
            "url": file_url,
            "filename": attachment.original_filename,
            "markdown": f"![{attachment.original_filename}]({file_url})",
        }
    )


@login_required
def preview_markdown(request: HttpRequest) -> HttpResponse:
    """Render markdown text to sanitized HTML for live preview."""
    if not (
        request.user.has_perm("aa_kanban.basic_access")
        or request.user.has_perm("aa_kanban.create_ticket")
    ):
        raise PermissionDenied("Permission required to preview markdown.")

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    raw_text = request.POST.get("text", "")
    from aa_kanban.markdown import render_markdown

    html = render_markdown(raw_text)
    if not html:
        html = f'<em class="text-muted">{_("Nothing to preview.")}</em>'
    return HttpResponse(html)
