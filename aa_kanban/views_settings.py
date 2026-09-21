from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .models import KanbanGroup


@login_required
@permission_required("aa_kanban.manage_boards", raise_exception=True)
def kanban_settings(request: HttpRequest) -> HttpResponse:
    """Render the main settings page with the list of Kanban groups."""
    groups = KanbanGroup.objects.prefetch_related("members").order_by("name")
    context = {
        "title": "Kanban Instellingen",
        "groups": groups,
    }
    return render(request, "aa_kanban/settings.html", context)


@login_required
@permission_required("aa_kanban.manage_boards", raise_exception=True)
def create_kanban_group(request: HttpRequest) -> HttpResponse:
    """HTMX endpoint to create a new KanbanGroup."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            KanbanGroup.objects.get_or_create(name=name)
    
    groups = KanbanGroup.objects.prefetch_related("members").order_by("name")
    return render(request, "aa_kanban/partials/group_list.html", {"groups": groups})


@login_required
@permission_required("aa_kanban.manage_boards", raise_exception=True)
def delete_kanban_group(request: HttpRequest, group_id: int) -> HttpResponse:
    """HTMX endpoint to delete a KanbanGroup."""
    if request.method == "POST":
        group = get_object_or_404(KanbanGroup, pk=group_id)
        group.delete()
    
    groups = KanbanGroup.objects.prefetch_related("members").order_by("name")
    return render(request, "aa_kanban/partials/group_list.html", {"groups": groups})


@login_required
@permission_required("aa_kanban.manage_boards", raise_exception=True)
def group_users_modal(request: HttpRequest, group_id: int) -> HttpResponse:
    """HTMX endpoint to render the user management modal for a group."""
    group = get_object_or_404(KanbanGroup, pk=group_id)
    all_users = User.objects.exclude(pk__in=group.members.values_list('pk', flat=True)).order_by('username')
    context = {
        "group": group,
        "members": group.members.order_by('username'),
        "all_users": all_users,
    }
    return render(request, "aa_kanban/partials/group_users_modal.html", context)


@login_required
@permission_required("aa_kanban.manage_boards", raise_exception=True)
def add_user_to_group(request: HttpRequest, group_id: int) -> HttpResponse:
    """HTMX endpoint to add a user to a KanbanGroup."""
    group = get_object_or_404(KanbanGroup, pk=group_id)
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            group.members.add(user)
    
    all_users = User.objects.exclude(pk__in=group.members.values_list('pk', flat=True)).order_by('username')
    context = {
        "group": group,
        "members": group.members.order_by('username'),
        "all_users": all_users,
    }
    return render(request, "aa_kanban/partials/group_users_modal.html", context)


@login_required
@permission_required("aa_kanban.manage_boards", raise_exception=True)
def remove_user_from_group(request: HttpRequest, group_id: int, user_id: int) -> HttpResponse:
    """HTMX endpoint to remove a user from a KanbanGroup."""
    group = get_object_or_404(KanbanGroup, pk=group_id)
    if request.method == "POST":
        user = get_object_or_404(User, pk=user_id)
        group.members.remove(user)
    
    all_users = User.objects.exclude(pk__in=group.members.values_list('pk', flat=True)).order_by('username')
    context = {
        "group": group,
        "members": group.members.order_by('username'),
        "all_users": all_users,
    }
    return render(request, "aa_kanban/partials/group_users_modal.html", context)
