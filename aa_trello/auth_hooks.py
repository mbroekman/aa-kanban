"""Alliance Auth hooks for aa_trello."""

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class AaTrelloMenuItem(MenuItemHook):
    """Menu item hook for aa_trello."""

    def __init__(self):
        super().__init__(
            "Trello",
            "fas fa-columns fa-fw",
            "aa_trello:index",
            navactive=["aa_trello:"],
        )

    def render(self, request):
        if request.user.has_perm("aa_trello.basic_access"):
            return super().render(request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return AaTrelloMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "aa_trello", r"^trello/")
