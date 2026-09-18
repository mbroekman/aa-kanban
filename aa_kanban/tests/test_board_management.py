"""Tests for frontend board/list/card management (TASK-1.8)."""

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse

from aa_kanban.models import Board, Card, List

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user_factory(db):
    """Create test users with basic_access permission."""
    _char_id = 9000

    def create_user(username: str, extra_perms: list[str] | None = None):
        nonlocal _char_id
        _char_id += 1
        user = AuthUtils.create_user(username)
        AuthUtils.add_main_character(user, f"Char {username}", character_id=_char_id)
        AuthUtils.add_permission_to_user_by_name("aa_kanban.basic_access", user)
        for perm in extra_perms or []:
            AuthUtils.add_permission_to_user_by_name(perm, user)
        return user

    return create_user


@pytest.fixture
def board_data(user_factory):
    """Set up a board with groups and one list."""
    manager = user_factory("mgr_user", extra_perms=["aa_kanban.manage_boards"])
    plain_user = user_factory("plain_user")
    write_grp = Group.objects.create(name="BM Write Group")
    view_grp = Group.objects.create(name="BM View Group")
    write_user = user_factory("bm_write_user")
    write_user.groups.add(write_grp)

    board = Board.objects.create(
        name="Test Board", slug="test-board", created_by=manager
    )
    board.write_groups.add(write_grp)
    board.view_groups.add(view_grp)

    k_list = List.objects.create(board=board, name="Backlog", order=0)

    return {
        "manager": manager,
        "plain_user": plain_user,
        "write_user": write_user,
        "write_grp": write_grp,
        "view_grp": view_grp,
        "board": board,
        "list": k_list,
    }


# ---------------------------------------------------------------------------
# create_board
# ---------------------------------------------------------------------------


class TestCreateBoard:
    def test_get_form_requires_manage_boards(self, user_factory):
        """Users without manage_boards cannot access create_board."""
        client = Client()
        client.force_login(user_factory("no_manage"))
        url = reverse("aa_kanban:create_board")
        resp = client.get(url)
        assert resp.status_code == 403

    def test_get_form_allowed_for_manager(self, user_factory):
        client = Client()
        manager = user_factory("mgr_get", extra_perms=["aa_kanban.manage_boards"])
        client.force_login(manager)
        url = reverse("aa_kanban:create_board")
        resp = client.get(url)
        assert resp.status_code == 200
        assert b"New Kanban Board" in resp.content or b"form" in resp.content

    def test_post_creates_board_and_redirects(self, user_factory):
        client = Client()
        manager = user_factory("mgr_post", extra_perms=["aa_kanban.manage_boards"])
        grp = Group.objects.create(name="Post Test Group")
        client.force_login(manager)
        url = reverse("aa_kanban:create_board")
        resp = client.post(
            url,
            {
                "name": "New Board via Frontend",
                "description": "Created in test",
                "view_groups": [str(grp.pk)],
                "write_groups": [],
            },
        )
        assert resp.status_code == 302
        board = Board.objects.get(name="New Board via Frontend")
        assert board.created_by == manager
        assert board.view_groups.filter(pk=grp.pk).exists()

    def test_post_empty_name_returns_form_with_error(self, user_factory):
        client = Client()
        manager = user_factory("mgr_empty", extra_perms=["aa_kanban.manage_boards"])
        client.force_login(manager)
        url = reverse("aa_kanban:create_board")
        resp = client.post(url, {"name": "", "description": ""})
        assert resp.status_code == 200
        assert b"verplicht" in resp.content or b"error" in resp.content.lower()

    def test_unauthenticated_redirected(self):
        client = Client()
        resp = client.get(reverse("aa_kanban:create_board"))
        assert resp.status_code in (302, 403)


# ---------------------------------------------------------------------------
# edit_board
# ---------------------------------------------------------------------------


class TestEditBoard:
    def test_owner_can_edit(self, board_data):
        client = Client()
        client.force_login(board_data["manager"])
        url = reverse(
            "aa_kanban:edit_board", kwargs={"board_slug": board_data["board"].slug}
        )
        resp = client.post(
            url,
            {
                "name": "Renamed Board",
                "description": "Updated desc",
                "view_groups": [],
                "write_groups": [],
            },
        )
        assert resp.status_code == 302
        board_data["board"].refresh_from_db()
        assert board_data["board"].name == "Renamed Board"

    def test_non_owner_without_manage_boards_denied(self, board_data):
        client = Client()
        client.force_login(board_data["plain_user"])
        url = reverse(
            "aa_kanban:edit_board", kwargs={"board_slug": board_data["board"].slug}
        )
        resp = client.post(
            url,
            {
                "name": "Hacked",
                "description": "",
                "view_groups": [],
                "write_groups": [],
            },
        )
        assert resp.status_code == 403

    def test_get_form_shows_current_values(self, board_data):
        client = Client()
        client.force_login(board_data["manager"])
        url = reverse(
            "aa_kanban:edit_board", kwargs={"board_slug": board_data["board"].slug}
        )
        resp = client.get(url)
        assert resp.status_code == 200
        assert b"Test Board" in resp.content


# ---------------------------------------------------------------------------
# delete_board
# ---------------------------------------------------------------------------


class TestDeleteBoard:
    def test_owner_can_delete(self, board_data):
        client = Client()
        client.force_login(board_data["manager"])
        slug = board_data["board"].slug
        url = reverse("aa_kanban:delete_board", kwargs={"board_slug": slug})
        resp = client.post(url)
        assert resp.status_code == 302
        assert not Board.objects.filter(slug=slug).exists()

    def test_plain_user_cannot_delete(self, board_data):
        client = Client()
        client.force_login(board_data["plain_user"])
        url = reverse(
            "aa_kanban:delete_board", kwargs={"board_slug": board_data["board"].slug}
        )
        resp = client.post(url)
        assert resp.status_code == 403
        assert Board.objects.filter(slug=board_data["board"].slug).exists()

    def test_get_redirects_to_board(self, board_data):
        """GET on delete_board should not delete, just redirect."""
        client = Client()
        client.force_login(board_data["manager"])
        url = reverse(
            "aa_kanban:delete_board", kwargs={"board_slug": board_data["board"].slug}
        )
        resp = client.get(url)
        assert resp.status_code == 302
        assert Board.objects.filter(slug=board_data["board"].slug).exists()


# ---------------------------------------------------------------------------
# create_list
# ---------------------------------------------------------------------------


class TestCreateList:
    def test_write_user_creates_list(self, board_data):
        client = Client()
        client.force_login(board_data["write_user"])
        url = reverse(
            "aa_kanban:create_list", kwargs={"board_slug": board_data["board"].slug}
        )
        resp = client.post(url, {"name": "New Column"})
        assert resp.status_code == 200
        assert List.objects.filter(
            board=board_data["board"], name="New Column"
        ).exists()

    def test_read_only_user_denied(self, board_data):
        client = Client()
        client.force_login(board_data["plain_user"])
        url = reverse(
            "aa_kanban:create_list", kwargs={"board_slug": board_data["board"].slug}
        )
        resp = client.post(url, {"name": "Sneaky Column"})
        assert resp.status_code == 403

    def test_empty_name_returns_400(self, board_data):
        client = Client()
        client.force_login(board_data["write_user"])
        url = reverse(
            "aa_kanban:create_list", kwargs={"board_slug": board_data["board"].slug}
        )
        resp = client.post(url, {"name": ""})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# rename_list
# ---------------------------------------------------------------------------


class TestRenameList:
    def test_write_user_renames_list(self, board_data):
        client = Client()
        client.force_login(board_data["write_user"])
        url = reverse(
            "aa_kanban:rename_list", kwargs={"list_id": board_data["list"].id}
        )
        resp = client.post(url, {"name": "Renamed Column"})
        assert resp.status_code == 200
        board_data["list"].refresh_from_db()
        assert board_data["list"].name == "Renamed Column"

    def test_read_only_user_denied(self, board_data):
        client = Client()
        client.force_login(board_data["plain_user"])
        url = reverse(
            "aa_kanban:rename_list", kwargs={"list_id": board_data["list"].id}
        )
        resp = client.post(url, {"name": "Hacked Name"})
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# delete_list
# ---------------------------------------------------------------------------


class TestDeleteList:
    def test_write_user_deletes_list(self, board_data):
        client = Client()
        client.force_login(board_data["write_user"])
        list_id = board_data["list"].id
        url = reverse("aa_kanban:delete_list", kwargs={"list_id": list_id})
        resp = client.post(url)
        assert resp.status_code == 200
        assert not List.objects.filter(pk=list_id).exists()

    def test_read_only_user_denied(self, board_data):
        client = Client()
        client.force_login(board_data["plain_user"])
        url = reverse(
            "aa_kanban:delete_list", kwargs={"list_id": board_data["list"].id}
        )
        resp = client.post(url)
        assert resp.status_code == 403
        assert List.objects.filter(pk=board_data["list"].id).exists()


# ---------------------------------------------------------------------------
# create_card
# ---------------------------------------------------------------------------


class TestCreateCard:
    def test_write_user_creates_card(self, board_data):
        client = Client()
        client.force_login(board_data["write_user"])
        url = reverse(
            "aa_kanban:create_card", kwargs={"list_id": board_data["list"].id}
        )
        resp = client.post(url, {"title": "New Test Card"})
        assert resp.status_code == 200
        assert Card.objects.filter(
            list=board_data["list"], title="New Test Card"
        ).exists()

    def test_card_returned_in_partial(self, board_data):
        client = Client()
        client.force_login(board_data["write_user"])
        url = reverse(
            "aa_kanban:create_card", kwargs={"list_id": board_data["list"].id}
        )
        resp = client.post(url, {"title": "Partial Card"})
        assert b"Partial Card" in resp.content

    def test_read_only_user_denied(self, board_data):
        client = Client()
        client.force_login(board_data["plain_user"])
        url = reverse(
            "aa_kanban:create_card", kwargs={"list_id": board_data["list"].id}
        )
        resp = client.post(url, {"title": "Sneaky Card"})
        assert resp.status_code == 403

    def test_empty_title_returns_400(self, board_data):
        client = Client()
        client.force_login(board_data["write_user"])
        url = reverse(
            "aa_kanban:create_card", kwargs={"list_id": board_data["list"].id}
        )
        resp = client.post(url, {"title": ""})
        assert resp.status_code == 400

    def test_card_order_increments(self, board_data):
        client = Client()
        client.force_login(board_data["write_user"])
        url = reverse(
            "aa_kanban:create_card", kwargs={"list_id": board_data["list"].id}
        )
        client.post(url, {"title": "Card One"})
        client.post(url, {"title": "Card Two"})
        cards = list(Card.objects.filter(list=board_data["list"]).order_by("order"))
        orders = [c.order for c in cards]
        assert orders == sorted(orders)
        assert len(set(orders)) == len(orders)
