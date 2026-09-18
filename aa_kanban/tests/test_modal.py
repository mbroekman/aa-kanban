"""Tests for card modal, comments, assignees and card editing."""

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse

from aa_kanban.models import Board, Card, Comment, List


@pytest.fixture
def user_factory(db):
    """Create test users with alliance auth main characters."""
    _char_id = 3000

    def create_user(username: str):
        nonlocal _char_id
        _char_id += 1
        user = AuthUtils.create_user(username)
        AuthUtils.add_main_character(
            user, f"Char {username}", character_id=_char_id
        )
        AuthUtils.add_permission_to_user_by_name(
            "aa_kanban.basic_access", user
        )
        return user

    return create_user


@pytest.fixture
def setup_modal_data(user_factory):
    """Set up boards, lists, cards, and permission groups."""
    creator = user_factory("modal_creator")
    view_grp = Group.objects.create(name="Modal View Group")
    write_grp = Group.objects.create(name="Modal Write Group")

    board = Board.objects.create(
        name="Modal Board", slug="modal-board", created_by=creator
    )
    board.view_groups.add(view_grp)
    board.write_groups.add(write_grp)

    k_list = List.objects.create(board=board, name="Sprint Backlog", order=0)
    card = Card.objects.create(
        list=k_list,
        title="Implement Auth Hook",
        description="Detailed specification for auth hook.",
        order=0,
        created_by=creator,
    )

    return {
        "creator": creator,
        "view_grp": view_grp,
        "write_grp": write_grp,
        "board": board,
        "list": k_list,
        "card": card,
    }


@pytest.mark.django_db
class TestCardModal:
    def test_card_modal_unauthenticated(self, setup_modal_data):
        data = setup_modal_data
        client = Client()
        url = reverse(
            "aa_kanban:card_modal", kwargs={"card_id": data["card"].id}
        )
        response = client.get(url)
        assert response.status_code == 302

    def test_card_modal_no_basic_access(self, setup_modal_data):
        data = setup_modal_data
        unauth_user = AuthUtils.create_user("no_basic_access_modal")
        AuthUtils.add_main_character(unauth_user, "NoAccessModalChar", 992211)
        client = Client()
        client.force_login(unauth_user)

        url = reverse(
            "aa_kanban:card_modal", kwargs={"card_id": data["card"].id}
        )
        response = client.get(url)
        assert response.status_code == 403

    def test_card_modal_view_only_user(self, user_factory, setup_modal_data):
        data = setup_modal_data
        viewer = user_factory("modal_viewer")
        viewer.groups.add(data["view_grp"])

        client = Client()
        client.force_login(viewer)

        url = reverse(
            "aa_kanban:card_modal", kwargs={"card_id": data["card"].id}
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["can_write"] is False
        assert "Implement Auth Hook" in response.content.decode()
        # Ensure edit form is not present for view-only users
        assert b"Save Description" not in response.content

    def test_card_modal_write_user(self, user_factory, setup_modal_data):
        data = setup_modal_data
        writer = user_factory("modal_writer")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:card_modal", kwargs={"card_id": data["card"].id}
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["can_write"] is True
        assert b"Save Description" in response.content
        assert b"Write a comment..." in response.content

    def test_card_modal_access_denied_without_view_group(
        self, user_factory, setup_modal_data
    ):
        data = setup_modal_data
        outsider = user_factory("modal_outsider")
        client = Client()
        client.force_login(outsider)

        url = reverse(
            "aa_kanban:card_modal", kwargs={"card_id": data["card"].id}
        )
        response = client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestCardComments:
    def test_add_comment_success(self, user_factory, setup_modal_data):
        data = setup_modal_data
        writer = user_factory("commenter_writer")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:add_comment", kwargs={"card_id": data["card"].id}
        )
        response = client.post(url, {"comment": "Looking solid, ready for PR."})
        assert response.status_code == 200
        assert b"Looking solid, ready for PR." in response.content
        assert b"commenter_writer" in response.content

        # Verify persisted in database
        assert (
            Comment.objects.filter(
                card=data["card"], text="Looking solid, ready for PR."
            ).count()
            == 1
        )

    def test_add_comment_read_only_denied(
        self, user_factory, setup_modal_data
    ):
        data = setup_modal_data
        viewer = user_factory("commenter_viewer")
        viewer.groups.add(data["view_grp"])

        client = Client()
        client.force_login(viewer)

        url = reverse(
            "aa_kanban:add_comment", kwargs={"card_id": data["card"].id}
        )
        response = client.post(url, {"comment": "Attempt by view only user"})
        assert response.status_code == 403
        assert Comment.objects.count() == 0

    def test_add_comment_empty_text(self, user_factory, setup_modal_data):
        data = setup_modal_data
        writer = user_factory("commenter_empty")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:add_comment", kwargs={"card_id": data["card"].id}
        )
        response = client.post(url, {"comment": "   "})
        assert response.status_code == 400


@pytest.mark.django_db
class TestCardAssigneesAndUpdates:
    def test_toggle_assignee_success(self, user_factory, setup_modal_data):
        data = setup_modal_data
        writer = user_factory("assign_writer")
        writer.groups.add(data["write_grp"])

        assignee = user_factory("pilot_assignee")

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:toggle_assignee", kwargs={"card_id": data["card"].id}
        )

        # Add assignee
        response1 = client.post(url, {"user_id": assignee.id})
        assert response1.status_code == 200
        assert data["card"].assignees.filter(pk=assignee.pk).exists()
        assert b"pilot_assignee" in response1.content

        # Toggle again to remove assignee
        response2 = client.post(url, {"user_id": assignee.id})
        assert response2.status_code == 200
        assert not data["card"].assignees.filter(pk=assignee.pk).exists()

    def test_toggle_assignee_read_only_denied(
        self, user_factory, setup_modal_data
    ):
        data = setup_modal_data
        viewer = user_factory("assign_viewer")
        viewer.groups.add(data["view_grp"])
        target = user_factory("assign_target")

        client = Client()
        client.force_login(viewer)

        url = reverse(
            "aa_kanban:toggle_assignee", kwargs={"card_id": data["card"].id}
        )
        response = client.post(url, {"user_id": target.id})
        assert response.status_code == 403

    def test_update_card_success(self, user_factory, setup_modal_data):
        data = setup_modal_data
        writer = user_factory("editor_writer")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:update_card", kwargs={"card_id": data["card"].id}
        )
        response = client.post(
            url,
            {
                "title": "New Title",
                "description": "Updated detailed description.",
            },
        )
        assert response.status_code == 200
        data["card"].refresh_from_db()
        assert data["card"].title == "New Title"
        assert data["card"].description == "Updated detailed description."

    def test_update_card_read_only_denied(
        self, user_factory, setup_modal_data
    ):
        data = setup_modal_data
        viewer = user_factory("editor_viewer")
        viewer.groups.add(data["view_grp"])

        client = Client()
        client.force_login(viewer)

        url = reverse(
            "aa_kanban:update_card", kwargs={"card_id": data["card"].id}
        )
        response = client.post(url, {"title": "Hacked Title"})
        assert response.status_code == 403
        data["card"].refresh_from_db()
        assert data["card"].title != "Hacked Title"
