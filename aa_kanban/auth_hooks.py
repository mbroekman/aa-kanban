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
    return UrlHook(urls, "aa_kanban", r"^kanban/")


@hooks.register("discord_cogs_hook")
def register_cogs():
    return ["aa_kanban.cogs"]
