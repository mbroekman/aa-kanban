"""Tests for aa_kanban API endpoints."""

import json

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from aa_kanban.models import KanbanGroup as Group
from django.test import Client
from unittest.mock import patch
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
        viewer.kanban_groups.add(data["view_grp"])  # Read-only group

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
        writer.kanban_groups.add(data["write_grp"])

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
        writer.kanban_groups.add(data["write_grp"])

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
        writer.kanban_groups.add(data["write_grp"])

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
        writer.kanban_groups.add(data["write_grp"])

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
        writer.kanban_groups.add(data["write_grp"])

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
        writer.kanban_groups.add(data["write_grp"])

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

    def test_move_card_webhook(self, user_factory, setup_api_data):
        data = setup_api_data
        writer = user_factory("board_writer_webhook")
        writer.kanban_groups.add(data["write_grp"])
        
        # Set up webhook
        board = data["board1"]
        board.discord_webhook_cards = "https://discord.com/api/webhooks/test-cards"
        board.save()

        client = Client()
        client.force_login(writer)

        url = reverse(
            "aa_kanban:move_card", kwargs={"card_id": data["card0"].id}
        )
        
        with patch("aa_kanban.utils.send_discord_webhook") as mock_send:
            response = client.post(
                url, {"target_list_id": data["list_b"].id, "new_position": 0}
            )
            assert response.status_code == 200
            mock_send.assert_called_once_with(
                "https://discord.com/api/webhooks/test-cards",
                "Card moved: **Card 0** was moved from `List A` to `List B`."
            )


@pytest.mark.django_db
class TestLabelEndpoints:
    def test_create_label(self, client, setup_api_data, user_factory):
        data = setup_api_data
        url = reverse("aa_kanban:create_label", args=[data["board1"].slug])
        
        # User without write access
        viewer = user_factory("label_viewer")
        viewer.kanban_groups.add(data["view_grp"])
        client.force_login(viewer)
        response = client.post(url, {"name": "Test", "color": "danger"})
        assert response.status_code == 403
        
        # User with write access
        writer = user_factory("label_writer")
        writer.kanban_groups.add(data["write_grp"])
        client.force_login(writer)
        
        response = client.post(url, {"name": "Test Label", "color": "success"})
        assert response.status_code == 200
        assert data["board1"].labels.filter(name="Test Label", color="success").exists()
        
    def test_toggle_label(self, client, setup_api_data, user_factory):
        from aa_kanban.models import Label
        data = setup_api_data
        label = Label.objects.create(board=data["board1"], name="Bug", color="danger")
        url = reverse("aa_kanban:toggle_label", args=[data["card0"].id])
        
        writer = user_factory("toggle_writer")
        writer.kanban_groups.add(data["write_grp"])
        client.force_login(writer)
        
        # Add label
        response = client.post(url, {"label_id": label.id})
        assert response.status_code == 200
        assert label in data["card0"].labels.all()
        
        # Remove label
        response = client.post(url, {"label_id": label.id})
        assert response.status_code == 200
        assert label not in data["card0"].labels.all()
@pytest.mark.django_db
class TestToggleAssignee:
    def test_toggle_assignee_add_and_remove(self, client, setup_api_data, user_factory):
        data = setup_api_data
        url = reverse("aa_kanban:toggle_assignee", args=[data["card0"].id])
        
        writer = user_factory("toggle_assignee_writer")
        writer.kanban_groups.add(data["write_grp"])
        client.force_login(writer)
        
        target_user = user_factory("target_assignee")
        
        with patch("aadiscordbot.tasks.send_direct_message_by_user_id.delay") as mock_send_dm:
            # Assign user
            response = client.post(url, {"user_id": target_user.id})
            assert response.status_code == 200
            assert target_user in data["card0"].assignees.all()
            mock_send_dm.assert_called_once_with(
                target_user.id, 
                "You have been assigned to the card: **Card 0** on board **Board One**."
            )
            
            mock_send_dm.reset_mock()
            
            # Remove user
            response = client.post(url, {"user_id": target_user.id})
            assert response.status_code == 200
            assert target_user not in data["card0"].assignees.all()
            mock_send_dm.assert_called_once_with(
                target_user.id, 
                "You have been removed from the card: **Card 0** on board **Board One**."
            )
