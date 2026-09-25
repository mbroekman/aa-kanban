"""Views for aa_kanban."""

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Board, Card, KanbanGroup, List
from .permissions import board_view_required


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def index(request: HttpRequest) -> HttpResponse:
    """Render the board overview listing boards visible to user."""
    boards = (
        Board.objects.visible_to(request.user)
        .select_related("created_by")
        .prefetch_related("view_groups", "write_groups")
        .annotate(list_count=Count("lists", distinct=True))
    )
    can_manage = request.user.has_perm("aa_kanban.manage_boards")
    all_groups = KanbanGroup.objects.order_by("name") if can_manage else KanbanGroup.objects.none()
    context = {
        "title": "Kanban Boards",
        "boards": boards,
        "can_manage": can_manage,
        "all_groups": all_groups,
    }
    return render(request, "aa_kanban/index.html", context)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@board_view_required
def board_detail(request: HttpRequest, board_slug: str, board: Board) -> HttpResponse:
    """Render the Kanban board detail page."""
    can_write = board.can_user_write(request.user)
    can_manage = request.user.has_perm("aa_kanban.manage_boards")

    lists = board.lists.prefetch_related(
        Prefetch(
            "cards",
            queryset=Card.objects.select_related("created_by").prefetch_related(
                "assignees", "labels"
            ),
        )
    )

    all_groups = (
        KanbanGroup.objects.order_by("name")
        if (can_write or can_manage)
        else KanbanGroup.objects.none()
    )

    context = {
        "title": board.name,
        "board": board,
        "lists": lists,
        "can_write": can_write,
        "can_manage": can_manage,
        "all_groups": all_groups,
    }
    return render(request, "aa_kanban/board_detail.html", context)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
@permission_required("aa_kanban.manage_boards", raise_exception=True)
def create_board(request: HttpRequest) -> HttpResponse:
    """Create a new Kanban board (manage_boards permission required)."""
    all_groups = KanbanGroup.objects.order_by("name")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        view_group_ids = request.POST.getlist("view_groups")
        write_group_ids = request.POST.getlist("write_groups")

        if not name:
            context = {
                "all_groups": all_groups,
                "error": "Board naam is verplicht.",
                "form_data": request.POST,
            }
            return render(request, "aa_kanban/partials/create_board_form.html", context)

        board = Board.objects.create(
            name=name,
            description=description,
            created_by=request.user,  # type: ignore[misc]
        )
        if view_group_ids:
            board.view_groups.set(KanbanGroup.objects.filter(pk__in=view_group_ids))
        if write_group_ids:
            board.write_groups.set(KanbanGroup.objects.filter(pk__in=write_group_ids))

        # Discord Webhook Notification
        from aa_kanban.models import KanbanSetting
        from aa_kanban.utils import send_discord_webhook
        
        kanban_settings = KanbanSetting.get_settings()
        if kanban_settings.board_creation_webhook:
            message = f"**New Kanban Board Created!**\nName: `{board.name}`\nCreated by: `{request.user.username}`"
            send_discord_webhook(kanban_settings.board_creation_webhook, message)

        url = redirect("aa_kanban:board_detail", board_slug=board.slug).url
        if request.headers.get("HX-Request"):
            response = HttpResponse(status=204)
            response["HX-Redirect"] = url
            return response
        return redirect(url)

    # GET: render form partial (used by HTMX)
    context = {"all_groups": all_groups}
    return render(request, "aa_kanban/partials/create_board_form.html", context)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def edit_board(request: HttpRequest, board_slug: str) -> HttpResponse:
    """Edit an existing board. Requires manage_boards or board ownership."""
    board = get_object_or_404(Board, slug=board_slug)

    if not (
        request.user.has_perm("aa_kanban.manage_boards")
        or board.created_by_id == request.user.pk
        or request.user.is_superuser
    ):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("You do not have permission to edit this board.")

    all_groups = KanbanGroup.objects.order_by("name")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        view_group_ids = request.POST.getlist("view_groups")
        write_group_ids = request.POST.getlist("write_groups")

        if not name:
            context = {
                "board": board,
                "all_groups": all_groups,
                "error": "Board naam is verplicht.",
                "form_data": request.POST,
            }
            return render(request, "aa_kanban/partials/edit_board_form.html", context)

        board.name = name
        board.description = description
        board.save(update_fields=["name", "description", "updated_at"])
        board.view_groups.set(KanbanGroup.objects.filter(pk__in=view_group_ids))
        board.write_groups.set(KanbanGroup.objects.filter(pk__in=write_group_ids))

        url = redirect("aa_kanban:board_detail", board_slug=board.slug).url
        if request.headers.get("HX-Request"):
            response = HttpResponse(status=204)
            response["HX-Redirect"] = url
            return response
        return redirect(url)

    # GET: render form partial (used by HTMX)
    context = {"board": board, "all_groups": all_groups}
    return render(request, "aa_kanban/partials/edit_board_form.html", context)


@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def delete_board(request: HttpRequest, board_slug: str) -> HttpResponse:
    """Delete a board. Requires manage_boards or board ownership."""
    board = get_object_or_404(Board, slug=board_slug)

    if not (
        request.user.has_perm("aa_kanban.manage_boards")
        or board.created_by_id == request.user.pk
        or request.user.is_superuser
    ):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("You do not have permission to delete this board.")

    if request.method == "POST":
        board.delete()
        url = redirect("aa_kanban:index").url
        if request.headers.get("HX-Request"):
            response = HttpResponse(status=204)
            response["HX-Redirect"] = url
            return response
        return redirect(url)

    url = redirect("aa_kanban:board_detail", board_slug=board.slug).url
    if request.headers.get("HX-Request"):
        response = HttpResponse(status=204)
        response["HX-Redirect"] = url
        return response
    return redirect(url)

@login_required
@permission_required("aa_kanban.basic_access", raise_exception=True)
def summary(request: HttpRequest) -> HttpResponse:
    """Render a summary of all accessible Kanban boards."""
    boards = (
        Board.objects.visible_to(request.user)
        .prefetch_related(
            Prefetch(
                "lists",
                queryset=List.objects.prefetch_related(
                    Prefetch(
                        "cards",
                        queryset=Card.objects.select_related("created_by").prefetch_related(
                            "assignees", "labels"
                        )
                    )
                )
            )
        )
    )
    
    context = {
        "title": "Kanban Summary",
        "boards": boards,
        "default_columns": ["Backlog", "To Do", "In Progress", "Review/Testing", "Done"]
    }
    return render(request, "aa_kanban/summary.html", context)

@login_required
def create_ticket(request: HttpRequest) -> HttpResponse:
    """Allow members to create tickets as cards on a designated ticket board."""
    from .models import KanbanSetting, Label, Board
    settings = KanbanSetting.get_settings()
    ticket_boards = settings.ticket_boards.all()
    if not ticket_boards.exists():
        # If no ticket board is configured, show an error message
        context = {"error": "Ticket system is currently unavailable. No ticket boards are configured."}
        return render(request, "aa_kanban/ticket_form.html", context)

    labels = Label.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        label_id = request.POST.get("label")
        board_id = request.POST.get("board")

        if not title:
            context = {"boards": ticket_boards, "labels": labels, "error": "Titel is verplicht."}
            return render(request, "aa_kanban/ticket_form.html", context)
            
        try:
            board = ticket_boards.get(pk=board_id)
        except Board.DoesNotExist:
            context = {"boards": ticket_boards, "labels": labels, "error": "Ongeldig ticket board geselecteerd."}
            return render(request, "aa_kanban/ticket_form.html", context)

        # Add to the "Backlog" column or first column
        list_obj = board.lists.filter(name="Backlog").first() or board.lists.first()
        if not list_obj:
            context = {"board": board, "labels": labels, "error": "Geen kolommen beschikbaar op het ticket board."}
            return render(request, "aa_kanban/ticket_form.html", context)

        card = Card.objects.create(
            list=list_obj,
            title=title,
            description=description,
            created_by=request.user
        )
        if label_id:
            try:
                card.labels.add(Label.objects.get(pk=label_id))
            except Label.DoesNotExist:
                pass
                
        if board.discord_webhook_cards:
            from aa_kanban.utils import send_discord_webhook
            url = request.build_absolute_uri(redirect("aa_kanban:board_detail", board_slug=board.slug).url)
            msg = f"**New Ticket Submitted!**\nTitle: `{card.title}`\nCreated by: `{request.user.username}`\n[View Board]({url})"
            send_discord_webhook(board.discord_webhook_cards, msg)

        return redirect("aa_kanban:ticket_success")

    context = {"boards": ticket_boards, "labels": labels}
    return render(request, "aa_kanban/ticket_form.html", context)

@login_required
def ticket_success(request: HttpRequest) -> HttpResponse:
    return render(request, "aa_kanban/ticket_success.html")
