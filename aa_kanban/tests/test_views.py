"""Tests for aa_kanban views."""

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from aa_kanban.models import KanbanGroup as Group
from django.test import Client
from django.urls import reverse
from unittest.mock import patch

from aa_kanban.models import Board, Card, KanbanSetting, Label, List


@pytest.fixture
def user_factory(db):
    _char_id = 1000

    def create_user(
        username, with_basic_access=True, with_main_character=True, **kwargs
    ):
        nonlocal _char_id
        _char_id += 1
        user = AuthUtils.create_user(username)
        if with_main_character:
            AuthUtils.add_main_character(
                user, f"Char {username}", character_id=_char_id
            )
        if with_basic_access:
            AuthUtils.add_permission_to_user_by_name(
                "aa_kanban.basic_access", user
            )
        return user

    return create_user


@pytest.fixture
def group_factory(db):
    def create_group(name):
        return Group.objects.create(name=name)

    return create_group


@pytest.fixture
def setup_boards(db, user_factory, group_factory):
    creator = user_factory("creator")
    view_grp = group_factory("View Group")
    write_grp = group_factory("Write Group")

    board1 = Board.objects.create(name="Alpha Board", created_by=creator)
    board1.view_groups.add(view_grp)

    board2 = Board.objects.create(name="Beta Board", created_by=creator)
    board2.write_groups.add(write_grp)

    board3 = Board.objects.create(name="Private Board", created_by=creator)

    # Add lists and cards to board1
    list1 = List.objects.create(board=board1, name="To Do", order=0)
    list2 = List.objects.create(board=board1, name="Done", order=1)

    label = Label.objects.create(board=board1, name="Bug", color="danger")
    card1 = Card.objects.create(list=list1, title="Card 1", order=0)
    card1.labels.add(label)
    Card.objects.create(list=list2, title="Card 2", order=0)

    return {
        "creator": creator,
        "view_grp": view_grp,
        "write_grp": write_grp,
        "board1": board1,
        "board2": board2,
        "board3": board3,
    }


@pytest.mark.django_db
class TestBoardListView:
    def test_unauthenticated_redirect(self):
        client = Client()
        response = client.get(reverse("aa_kanban:index"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_permission_denied_without_basic_access(self, user_factory):
        user = user_factory("no_basic", with_basic_access=False)
        client = Client()
        client.force_login(user)

        response = client.get(reverse("aa_kanban:index"))
        assert response.status_code == 403

    def test_board_list_filtering(self, user_factory, setup_boards):
        data = setup_boards
        user = user_factory("viewer")
        user.kanban_groups.add(data["view_grp"])

        client = Client()
        client.force_login(user)

        response = client.get(reverse("aa_kanban:index"))
        assert response.status_code == 200
        boards = list(response.context["boards"])

        assert data["board1"] in boards
        assert data["board2"] not in boards
        assert data["board3"] not in boards


@pytest.mark.django_db
class TestBoardDetailView:
    def test_board_detail_access_denied(self, user_factory, setup_boards):
        data = setup_boards
        user = user_factory("unauth_viewer")
        client = Client()
        client.force_login(user)

        url = reverse(
            "aa_kanban:board_detail", kwargs={"board_slug": data["board1"].slug}
        )
        response = client.get(url)
        assert response.status_code == 403

    def test_board_detail_read_only_access(self, user_factory, setup_boards):
        data = setup_boards
        user = user_factory("viewer")
        user.kanban_groups.add(data["view_grp"])

        client = Client()
        client.force_login(user)

        url = reverse(
            "aa_kanban:board_detail", kwargs={"board_slug": data["board1"].slug}
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["can_write"] is False
        assert response.context["board"] == data["board1"]
        assert len(response.context["lists"]) == 2

    def test_board_detail_write_access(self, user_factory, setup_boards):
        data = setup_boards
        user = user_factory("writer")
        user.kanban_groups.add(data["write_grp"])

        client = Client()
        client.force_login(user)

        url = reverse(
            "aa_kanban:board_detail", kwargs={"board_slug": data["board2"].slug}
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["can_write"] is True
        assert response.context["board"] == data["board2"]

    def test_board_detail_query_efficiency(
        self, user_factory, setup_boards, django_assert_num_queries
    ):
        data = setup_boards
        user = user_factory("viewer")
        user.kanban_groups.add(data["view_grp"])

        client = Client()
        client.force_login(user)

        url = reverse(
            "aa_kanban:board_detail", kwargs={"board_slug": data["board1"].slug}
        )

        # Warm up DB state (custom CSS and Alliance Auth menu item initialization)
        client.get(url)

        # Baseline queries for board detail view
        with django_assert_num_queries(25):
            response = client.get(url)
            assert response.status_code == 200

        # Add additional lists and cards
        new_list = List.objects.create(
            board=data["board1"], name="Review", order=3
        )
        for i in range(5):
            c = Card.objects.create(
                list=new_list, title=f"Extra Card {i}", order=i
            )
            c.assignees.add(user)

        # Query count remains exactly the same (no N+1 when adding cards/lists)
        with django_assert_num_queries(25):
            response2 = client.get(url)
            assert response2.status_code == 200

    def test_create_board_webhook(self, client, setup_boards):
        """Test that creating a board triggers the webhook."""
        data = setup_boards
        creator = data["creator"]
        from allianceauth.tests.auth_utils import AuthUtils
        AuthUtils.add_permission_to_user_by_name("aa_kanban.manage_boards", creator)
        client.force_login(creator)
        
        # Set up global webhook
        setting = KanbanSetting.get_settings()
        setting.board_creation_webhook = "https://discord.com/api/webhooks/test"
        setting.save()
        
        url = reverse("aa_kanban:create_board")
        post_data = {
            "name": "Webhook Board",
            "description": "Test",
        }
        
        with patch("aa_kanban.utils.send_discord_webhook") as mock_send:
            response = client.post(url, post_data)
            assert response.status_code == 302
            mock_send.assert_called_once_with("https://discord.com/api/webhooks/test", "**New Kanban Board Created!**\nName: `Webhook Board`\nCreated by: `creator`")
