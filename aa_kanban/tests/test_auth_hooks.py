"""Tests for aa_kanban auth_hooks."""

import pytest
from django.contrib.auth.models import Permission, User
from django.test import RequestFactory

from aa_kanban import __version__, auth_hooks


@pytest.fixture
def user_with_basic_access(db):
    user = User.objects.create_user(username="basic_user", email="basic@example.com")
    perm = Permission.objects.get(
        codename="basic_access", content_type__app_label="aa_kanban"
    )
    user.user_permissions.add(perm)
    return user


@pytest.fixture
def user_without_basic_access(db):
    return User.objects.create_user(
        username="no_access_user", email="no_access@example.com"
    )


@pytest.mark.django_db
class TestAuthHooks:
    def test_menu_item_render_with_permission(self, user_with_basic_access):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user_with_basic_access

        menu_item = auth_hooks.AaKanbanMenuItem()
        rendered = menu_item.render(request)
        assert rendered != ""
        assert "Kanban" in rendered

    def test_menu_item_render_without_permission(self, user_without_basic_access):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user_without_basic_access

        menu_item = auth_hooks.AaKanbanMenuItem()
        rendered = menu_item.render(request)
        assert rendered == ""

    def test_register_hooks(self):
        menu = auth_hooks.register_menu()
        assert isinstance(menu, auth_hooks.AaKanbanMenuItem)

        url_hook = auth_hooks.register_urls()
        assert url_hook.include_pattern.app_name == "aa_kanban"
        assert "kanban" in str(url_hook.include_pattern.pattern)

    def test_bs5_menu_item_shows_version_badge(self, user_with_basic_access):
        request = RequestFactory().get("/")
        request.user = user_with_basic_access

        menu_item = auth_hooks.AaKanbanMenuItem()
        # AA's sidebar renderer sets this template right before render()
        menu_item.template = auth_hooks.AA_BS5_MENU_ITEM_TEMPLATE
        rendered = menu_item.render(request)

        assert "aa-kanban-menu-version" in rendered
        assert f"v{__version__}" in rendered
        assert "Kanban" in rendered

    def test_bs5_menu_item_hidden_without_permission(self, user_without_basic_access):
        request = RequestFactory().get("/")
        request.user = user_without_basic_access

        menu_item = auth_hooks.AaKanbanMenuItem()
        menu_item.template = auth_hooks.AA_BS5_MENU_ITEM_TEMPLATE
        assert menu_item.render(request) == ""

    def test_menu_item_text_unchanged(self):
        # Text/class must stay stable so AA's MenuItem hash sync creates no duplicates
        menu_item = auth_hooks.AaKanbanMenuItem()
        assert __version__ not in str(menu_item.text)
