"""Admin configuration for aa_kanban.

Business-functionaliteit (boards, lijsten, cards, labels) wordt beheerd via
de frontend. De admin is hier read-only voor overzicht/debug. Alleen Comments
blijven bewerkbaar voor moderatie-doeleinden.
"""

from django.contrib import admin

from .models import Board, Card, Comment, Label, List


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Read-only board overview. Manage boards via the frontend."""

    list_display = ("name", "slug", "created_by", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = (
        "name",
        "slug",
        "description",
        "view_groups",
        "write_groups",
        "created_by",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request) -> bool:  # type: ignore[override]
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    """Read-only list overview. Manage columns via the board frontend."""

    list_display = ("name", "board", "order", "created_at")
    list_filter = ("board",)
    search_fields = ("name", "board__name")
    readonly_fields = ("name", "board", "order", "created_at", "updated_at")

    def has_add_permission(self, request) -> bool:  # type: ignore[override]
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    """Read-only label overview. Manage labels via the board frontend."""

    list_display = ("name", "color", "board")
    list_filter = ("board", "color")
    search_fields = ("name", "board__name")
    readonly_fields = ("name", "color", "board")

    def has_add_permission(self, request) -> bool:  # type: ignore[override]
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """Read-only card overview. Manage cards via the board frontend."""

    list_display = ("title", "list", "order", "due_date", "created_at")
    list_filter = ("list__board", "list")
    search_fields = ("title", "description")
    readonly_fields = (
        "title",
        "description",
        "list",
        "order",
        "assignees",
        "labels",
        "due_date",
        "created_by",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request) -> bool:  # type: ignore[override]
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comments are manageable from admin for moderation purposes."""

    list_display = ("card", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "author__username", "card__title")
    readonly_fields = ("created_at",)
