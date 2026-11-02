"""Admin configuration for aa_kanban.

Business-functionaliteit (boards, lijsten, cards, labels) wordt beheerd via
de frontend. De admin is hier read-only voor overzicht/debug. Alleen Comments
blijven bewerkbaar voor moderatie-doeleinden.
"""

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from .models import (
    Board,
    Card,
    Comment,
    IntakeApiKey,
    KanbanGroup,
    KanbanSetting,
    KanbanTeam,
    Label,
    List,
)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Read-only board overview, except for technical webhook settings."""

    list_display = (
        "name",
        "slug",
        "stale_card_alert_hours",
        "stale_card_repeat_hours",
        "created_by",
        "created_at",
        "updated_at",
    )
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

    # Allow changing so admins can edit webhooks
    def has_change_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return True

    def has_delete_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        return False


@admin.register(KanbanSetting)
class KanbanSettingAdmin(admin.ModelAdmin):
    """Global configuration for aa_kanban."""

    list_display = ("__str__", "board_creation_webhook")

    def has_add_permission(self, request) -> bool:  # type: ignore[override]
        # Only allow 1 instance
        from .models import KanbanSetting

        if KanbanSetting.objects.exists():
            return False
        return True


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

    list_display = ("name", "color")
    list_filter = ("color",)
    search_fields = ("name",)
    readonly_fields = ("name", "color")

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
        "last_stale_alert_at",
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


@admin.register(KanbanGroup)
class KanbanGroupAdmin(admin.ModelAdmin):
    """Manage kanban groups for board access control."""

    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("members", "groups")


@admin.register(KanbanTeam)
class KanbanTeamAdmin(admin.ModelAdmin):
    """Manage teams for ticket assignments."""

    list_display = ("name", "discord_role_id")
    search_fields = ("name",)
    filter_horizontal = ("members", "groups")


@admin.register(IntakeApiKey)
class IntakeApiKeyAdmin(admin.ModelAdmin):
    """API keys for the Discord thread router (technical setting, AGENTS §8)."""

    list_display = ("name", "prefix", "is_active", "created_at", "last_used_at")
    readonly_fields = ("prefix", "created_at", "last_used_at")
    fields = ("name", "is_active", "prefix", "created_at", "last_used_at")
    actions = ["regenerate_key"]

    def save_model(self, request, obj, form, change):
        raw_key = obj.set_new_key() if not change else None
        super().save_model(request, obj, form, change)
        if raw_key:
            self._show_key(request, obj, raw_key)

    def _show_key(self, request, obj, raw_key):
        messages.warning(
            request,
            _(
                "API key for {name}: {key} - copy it now into KANBAN_API_KEY of the"
                " router; it is not shown again."
            ).format(name=obj.name, key=raw_key),
        )

    @admin.action(description=_("Generate a new key (the old one stops working)"))
    def regenerate_key(self, request, queryset):
        for obj in queryset:
            raw_key = obj.set_new_key()
            obj.save(update_fields=["key_hash", "prefix"])
            self._show_key(request, obj, raw_key)
