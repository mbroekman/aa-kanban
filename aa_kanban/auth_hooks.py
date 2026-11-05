"""Alliance Auth hooks for aa_kanban."""

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook
from django.conf import settings

from . import urls


class AaKanbanMenuItem(MenuItemHook):
    """Menu item hook for aa_kanban."""

    def __init__(self):
        super().__init__(
            getattr(settings, "AA_KANBAN_APP_NAME", "Kanban"),
            "fas fa-columns fa-fw",
            "aa_kanban:index",
            navactive=["aa_kanban:"],
        )

    def render(self, request):
        if request.user.has_perm("aa_kanban.basic_access"):
            return super().render(request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return AaKanbanMenuItem()


class AaKanbanMembersMenuItem(MenuItemHook):
    """Menu item for the members page; its name is set in the Kanban settings."""

    def __init__(self):
        super().__init__(
            "Member Boards",
            "fas fa-users fa-fw",
            "aa_kanban:members_index",
            navactive=["aa_kanban:members_index"],
        )

    def render(self, request):
        if not request.user.has_perm("aa_kanban.basic_access"):
            return ""
        from .models import Board, KanbanSetting

        if not Board.objects.active().filter(is_members_board=True).exists():
            return ""
        self.text = KanbanSetting.get_settings().members_page_name
        return super().render(request)


@hooks.register("menu_item_hook")
def register_menu_members():
    return AaKanbanMembersMenuItem()


class AaKanbanCreateTicketMenuItem(MenuItemHook):
    """Menu item hook for submitting a ticket."""

    def __init__(self):
        super().__init__(
            "Submit Ticket",
            "fas fa-ticket-alt fa-fw",
            "aa_kanban:create_ticket",
            navactive=["aa_kanban:create_ticket"],
        )

    def render(self, request):
        if request.user.has_perm("aa_kanban.create_ticket"):
            return super().render(request)
        return ""


@hooks.register("menu_item_hook")
def register_menu_create_ticket():
    return AaKanbanCreateTicketMenuItem()


@hooks.register("url_hook")
def register_urls():
    # The intake endpoint authenticates with an API key, not a login session.
    return UrlHook(
        urls,
        "aa_kanban",
        r"^kanban/",
        excluded_views=["aa_kanban.views_intake.discord_thread_intake"],
    )


@hooks.register("discord_cogs_hook")
def register_cogs():
    return ["aa_kanban.cogs"]
