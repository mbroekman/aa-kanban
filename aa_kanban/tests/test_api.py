"""Tests for aa_kanban API endpoints."""

import json

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse

from aa_kanban.models import Board, Card, List


@pytest.fixture
def user_factory(db):
    """Create test users with alliance auth main characters."""
    _char_id = 2000

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
def setup_api_data(user_factory):
    """Set up boards, lists, cards, and permission groups."""
    creator = user_factory("api_creator")
    view_grp = Group.objects.create(name="API View Group")
    write_grp = Group.objects.create(name="API Write Group")

    board1 = Board.objects.create(
        name="Board One", slug="board-one", created_by=creator
    )
    board1.view_groups.add(view_grp)
    board1.write_groups.add(write_grp)

    board2 = Board.objects.create(
        name="Board Two", slug="board-two", created_by=creator
    )

    list_a = List.objects.create(board=board1, name="List A", order=0)
    list_b = List.objects.create(board=board1, name="List B", order=1)
    list_other = List.objects.create(board=board2, name="List Other", order=0)

    card0 = Card.objects.create(
        list=list_a, title="Card 0", order=0, created_by=creator
    )
    card1 = Card.objects.create(
        list=list_a, title="Card 1", order=1, created_by=creator
    )
    card2 = Card.objects.create(
        list=list_a, title="Card 2", order=2, created_by=creator
    )

    card_b0 = Card.objects.create(
        list=list_b, title="Card B0", order=0, created_by=creator
    )

    return {
        "creator": creator,
        "view_grp": view_grp,
        "write_grp": write_grp,
        "board1": board1,
        "board2": board2,
        "list_a": list_a,
        "list_b": list_b,
        "list_other": list_other,
        "card0": card0,
        "card1": card1,
        "card2": card2,
        "card_b0": card_b0,
    }


@pytest.mark.django_db
class TestMoveCardAPI:
    def test_move_card_unauthenticated(self, setup_api_data):
        data = setup_api_data
        client = Client()
        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        response = client.post(
            url, {"target_list_id": data["list_a"].id, "new_position": 1}
        )
        # Unauthenticated users redirected to login
        assert response.status_code == 302

    def test_move_card_no_basic_access(self, setup_api_data):
        data = setup_api_data
        unauth_user = AuthUtils.create_user("no_basic_access_user")
        AuthUtils.add_main_character(unauth_user, "NoAccessChar", 887766)
        client = Client()
        client.force_login(unauth_user)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        response = client.post(
            url, {"target_list_id": data["list_a"].id, "new_position": 1}
        )
        assert response.status_code == 403

    def test_move_card_read_only_user_denied(
        self, user_factory, setup_api_data
    ):
        data = setup_api_data
        viewer = user_factory("board_viewer")
        viewer.groups.add(data["view_grp"])  # Read-only group

        client = Client()
        client.force_login(viewer)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        response = client.post(
            url, {"target_list_id": data["list_a"].id, "new_position": 1}
        )
        assert response.status_code == 403

    def test_move_card_method_not_allowed(self, user_factory, setup_api_data):
        data = setup_api_data
        writer = user_factory("board_writer_get")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        response = client.get(url)
        assert response.status_code == 405

    def test_move_card_within_same_list(self, user_factory, setup_api_data):
        data = setup_api_data
        writer = user_factory("board_writer_same")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        # Move card 0 to position 2 in list_a
        response = client.post(
            url, {"target_list_id": data["list_a"].id, "new_position": 2}
        )
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "success"
        assert json_data["new_position"] == 2

        # Check orders in DB: Card 1 should be 0, Card 2 should be 1, Card 0 should be 2
        cards_in_a = list(data["list_a"].cards.order_by("order"))
        assert [c.id for c in cards_in_a] == [
            data["card1"].id,
            data["card2"].id,
            data["card0"].id,
        ]
        assert [c.order for c in cards_in_a] == [0, 1, 2]

    def test_move_card_to_another_list(self, user_factory, setup_api_data):
        data = setup_api_data
        writer = user_factory("board_writer_other")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        # Move card 0 to list_b at position 0 (before card_b0)
        response = client.post(
            url, {"target_list_id": data["list_b"].id, "new_position": 0}
        )
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "success"
        assert json_data["target_list_id"] == data["list_b"].id
        assert json_data["new_position"] == 0

        # Check list A: card1 (0), card2 (1)
        cards_in_a = list(data["list_a"].cards.order_by("order"))
        assert [c.id for c in cards_in_a] == [data["card1"].id, data["card2"].id]
        assert [c.order for c in cards_in_a] == [0, 1]

        # Check list B: card0 (0), card_b0 (1)
        cards_in_b = list(data["list_b"].cards.order_by("order"))
        assert [c.id for c in cards_in_b] == [data["card0"].id, data["card_b0"].id]
        assert [c.order for c in cards_in_b] == [0, 1]

    def test_move_card_json_payload(self, user_factory, setup_api_data):
        data = setup_api_data
        writer = user_factory("board_writer_json")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card1"].id}
        )
        payload = json.dumps(
            {"target_list_id": data["list_b"].id, "new_position": 1}
        )
        response = client.post(url, payload, content_type="application/json")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_move_card_cross_board_blocked(self, user_factory, setup_api_data):
        data = setup_api_data
        writer = user_factory("board_writer_cross")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        # Attempt moving to a list on a completely different board
        response = client.post(
            url, {"target_list_id": data["list_other"].id, "new_position": 0}
        )
        assert response.status_code == 400
        assert b"does not belong to the same board" in response.content

    def test_move_card_invalid_inputs(self, user_factory, setup_api_data):
        data = setup_api_data
        writer = user_factory("board_writer_invalid")
        writer.groups.add(data["write_grp"])

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        # Missing position
        response = client.post(url, {"target_list_id": data["list_a"].id})
        assert response.status_code == 400

        # Non-integer position
        response = client.post(
            url, {"target_list_id": data["list_a"].id, "new_position": "invalid"}
        )
        assert response.status_code == 400
