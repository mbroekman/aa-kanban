"""Alliance Auth hooks for aa_kanban."""

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class AaKanbanMenuItem(MenuItemHook):
    """Menu item hook for aa_kanban."""

    def __init__(self):
        super().__init__(
            "Kanban",
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


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "aa_kanban", r"^kanban/")
