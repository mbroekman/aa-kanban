"""Views for aa_kanban."""

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.db.models import Count, Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Board, Card
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
    all_groups = Group.objects.order_by("name") if can_manage else Group.objects.none()
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
        Group.objects.order_by("name")
        if (can_write or can_manage)
        else Group.objects.none()
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
    all_groups = Group.objects.order_by("name")

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
            board.view_groups.set(Group.objects.filter(pk__in=view_group_ids))
        if write_group_ids:
            board.write_groups.set(Group.objects.filter(pk__in=write_group_ids))

        return redirect("aa_kanban:board_detail", board_slug=board.slug)

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

    all_groups = Group.objects.order_by("name")

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
        board.view_groups.set(Group.objects.filter(pk__in=view_group_ids))
        board.write_groups.set(Group.objects.filter(pk__in=write_group_ids))

        return redirect("aa_kanban:board_detail", board_slug=board.slug)

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
        return redirect("aa_kanban:index")

    return redirect("aa_kanban:board_detail", board_slug=board.slug)
