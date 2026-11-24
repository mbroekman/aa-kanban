"""Tests for the aa_kanban React/shadcn SPA host view and JSON API."""

import json
from unittest.mock import patch

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.urls import reverse

from aa_kanban.models import Board, Card, KanbanGroup, KanbanTeam, Label


@pytest.fixture
def basic_user(db):
    """User with aa_kanban.basic_access permission."""
    user = AuthUtils.create_user("spa_pilot")
    AuthUtils.add_main_character(user, "SPA Pilot", character_id=91001)
    AuthUtils.add_permission_to_user_by_name("aa_kanban.basic_access", user)
    return user


@pytest.fixture
def other_user(db):
    """Another user with basic_access but no board membership."""
    user = AuthUtils.create_user("spa_outsider")
    AuthUtils.add_main_character(user, "SPA Outsider", character_id=91002)
    AuthUtils.add_permission_to_user_by_name("aa_kanban.basic_access", user)
    return user


@pytest.fixture
def board_with_writer(db, basic_user):
    """Create a board where basic_user has write access via a KanbanGroup."""
    group = KanbanGroup.objects.create(name="SPA Writers")
    group.members.add(basic_user)
    board = Board.objects.create(name="SPA Ops", slug="spa-ops")
    board.write_groups.add(group)
    return board


@pytest.mark.django_db
def test_spa_host_view_renders_mount_point(client, basic_user):
    """Authorized user gets the SPA mount point and bundle references."""
    client.force_login(basic_user)
    resp = client.get(reverse("aa_kanban:spa_root"))
    assert resp.status_code == 200
    body = resp.content.decode()
    assert 'id="aa-kanban-spa"' in body
    assert "aa_kanban/spa/assets/index.js" in body
    assert "aa_kanban/spa/assets/index.css" in body

    sub_resp = client.get(
        reverse("aa_kanban:spa_subpath", kwargs={"subpath": "board/spa-ops/"})
    )
    assert sub_resp.status_code == 200


@pytest.mark.django_db
def test_api_boards_and_detail_permissions(
    client, basic_user, other_user, board_with_writer
):
    """Only authorized users see the board in api_boards and api_board_detail."""
    client.force_login(other_user)
    resp = client.get(reverse("aa_kanban:spa_api_boards"))
    assert resp.status_code == 200
    assert resp.json()["boards"] == []

    detail_resp = client.get(
        reverse(
            "aa_kanban:spa_api_board_detail",
            kwargs={"board_slug": board_with_writer.slug},
        )
    )
    assert detail_resp.status_code == 403

    client.force_login(basic_user)
    resp = client.get(reverse("aa_kanban:spa_api_boards"))
    assert resp.status_code == 200
    boards = resp.json()["boards"]
    assert len(boards) == 1
    assert boards[0]["slug"] == "spa-ops"
    assert boards[0]["can_write"] is True

    detail_resp = client.get(
        reverse(
            "aa_kanban:spa_api_board_detail",
            kwargs={"board_slug": board_with_writer.slug},
        )
    )
    assert detail_resp.status_code == 200
    payload = detail_resp.json()
    assert payload["board"]["slug"] == "spa-ops"
    assert len(payload["lists"]) == 5


@pytest.mark.django_db
def test_api_card_lifecycle_and_move(client, basic_user, board_with_writer):
    """Create list, create card, update, move, comment, search, and delete."""
    client.force_login(basic_user)
    label = Label.objects.create(name="Urgent", color="danger")
    team = KanbanTeam.objects.create(name="Logistics")

    # Create column
    list_resp = client.post(
        reverse(
            "aa_kanban:spa_api_create_list",
            kwargs={"board_slug": board_with_writer.slug},
        ),
        json.dumps({"name": "QA", "wip_limit": 2}),
        content_type="application/json",
    )
    assert list_resp.status_code == 201
    qa_list_id = list_resp.json()["list"]["id"]

    first_list = board_with_writer.lists.order_by("order").first()
    assert first_list is not None

    # Create card
    card_resp = client.post(
        reverse("aa_kanban:spa_api_create_card", kwargs={"list_id": first_list.pk}),
        json.dumps({"title": "Build Freighter"}),
        content_type="application/json",
    )
    assert card_resp.status_code == 201
    card_id = card_resp.json()["card"]["id"]

    # Update card
    upd_resp = client.post(
        reverse("aa_kanban:spa_api_update_card", kwargs={"card_id": card_id}),
        json.dumps(
            {
                "title": "Build Jump Freighter",
                "description": "**Ready** to build",
                "color": "info",
                "assigned_team_id": team.pk,
                "label_ids": [label.pk],
                "assignee_ids": [basic_user.pk],
            }
        ),
        content_type="application/json",
    )
    assert upd_resp.status_code == 200
    updated = upd_resp.json()["card"]
    assert updated["title"] == "Build Jump Freighter"
    assert updated["color"] == "info"
    assert updated["assigned_team"]["id"] == team.pk
    assert [lbl["id"] for lbl in updated["labels"]] == [label.pk]

    # Add comment
    cmt_resp = client.post(
        reverse("aa_kanban:spa_api_add_comment", kwargs={"card_id": card_id}),
        json.dumps({"text": "Minerals staged"}),
        content_type="application/json",
    )
    assert cmt_resp.status_code == 201
    assert cmt_resp.json()["comment"]["text"] == "Minerals staged"

    # Move card
    move_resp = client.post(
        reverse("aa_kanban:spa_api_move_card", kwargs={"card_id": card_id}),
        json.dumps({"target_list_id": qa_list_id, "new_position": 0}),
        content_type="application/json",
    )
    assert move_resp.status_code == 200
    card_obj = Card.objects.get(pk=card_id)
    assert card_obj.list_id == qa_list_id

    # Search
    search_resp = client.get(
        reverse("aa_kanban:spa_api_search"), {"q": "Jump Freighter"}
    )
    assert search_resp.status_code == 200
    assert len(search_resp.json()["results"]) == 1

    # Delete card
    del_resp = client.post(
        reverse("aa_kanban:spa_api_delete_card", kwargs={"card_id": card_id}),
        json.dumps({}),
        content_type="application/json",
    )
    assert del_resp.status_code == 200
    assert not Card.objects.filter(pk=card_id).exists()


@pytest.mark.django_db
def test_default_routes_serve_spa_and_settings_crud(client, basic_user):
    """Default routes render the SPA and settings/board CRUD endpoints work."""
    manager_group = KanbanGroup.objects.create(
        name="SPA Managers", can_manage_boards=True
    )
    manager_group.members.add(basic_user)
    client.force_login(basic_user)

    for url_name in (
        "aa_kanban:index",
        "aa_kanban:members_index",
        "aa_kanban:summary",
        "aa_kanban:settings",
        "aa_kanban:archived_boards",
    ):
        resp = client.get(reverse(url_name))
        assert resp.status_code == 200
        assert b'id="aa-kanban-spa"' in resp.content

    # Create board via SPA API
    b_resp = client.post(
        reverse("aa_kanban:spa_api_create_board"),
        json.dumps({"name": "API Board", "is_ticket_board": True}),
        content_type="application/json",
    )
    assert b_resp.status_code == 201
    slug = b_resp.json()["board"]["slug"]

    # Archive & restore board
    assert (
        client.post(
            reverse("aa_kanban:spa_api_archive_board", kwargs={"board_slug": slug}),
            json.dumps({}),
            content_type="application/json",
        ).status_code
        == 200
    )
    assert Board.objects.get(slug=slug).is_archived is True
    assert (
        client.post(
            reverse("aa_kanban:spa_api_restore_board", kwargs={"board_slug": slug}),
            json.dumps({}),
            content_type="application/json",
        ).status_code
        == 200
    )
    assert Board.objects.get(slug=slug).is_archived is False

    # Settings CRUD
    assert client.get(reverse("aa_kanban:spa_api_settings")).status_code == 200
    lbl_resp = client.post(
        reverse("aa_kanban:spa_api_save_label"),
        json.dumps({"name": "SPA Label", "color": "info", "is_ticket_label": True}),
        content_type="application/json",
    )
    assert lbl_resp.status_code == 200
    assert any(lbl["name"] == "SPA Label" for lbl in lbl_resp.json()["labels"])

    # Submit Ticket GET route renders SPA without VariableDoesNotExist
    AuthUtils.add_permission_to_user_by_name("aa_kanban.create_ticket", basic_user)
    basic_user.refresh_from_db()
    client.force_login(basic_user)
    ticket_resp = client.get(reverse("aa_kanban:create_ticket"))
    assert ticket_resp.status_code == 200
    assert b'id="aa-kanban-spa"' in ticket_resp.content


@pytest.mark.django_db
class TestMoveCardDiscordThreadPrompt:
    """TASK-121: the classic move_card view notifies a card's Discord
    thread on move and flags prompt_close_thread when the card lands in
    the board's last list - api_move_card (used by the SPA) must do the
    same instead of silently returning {"ok": True}."""

    @pytest.fixture
    def ticket_card(self, board_with_writer):
        list_todo = board_with_writer.lists.get(name="To Do")
        return Card.objects.create(
            list=list_todo,
            title="SPA Ticket with Thread",
            discord_thread_id=555666777,
        )

    def test_move_notifies_thread_and_does_not_prompt_mid_board(
        self, client, basic_user, board_with_writer, ticket_card
    ):
        target_list = board_with_writer.lists.get(name="In Progress")
        client.force_login(basic_user)

        with patch("aa_kanban.tasks.notify_ticket_thread.delay") as mock_notify:
            resp = client.post(
                reverse(
                    "aa_kanban:spa_api_move_card", kwargs={"card_id": ticket_card.id}
                ),
                json.dumps({"target_list_id": target_list.id, "new_position": 0}),
                content_type="application/json",
            )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["ok"] is True
        assert payload["prompt_close_thread"] is False

        assert mock_notify.called
        args, _kwargs = mock_notify.call_args
        assert args[0] == 555666777
        assert "To Do" in args[1]
        assert "In Progress" in args[1]
        assert basic_user.username in args[1]

    def test_move_to_last_list_prompts_thread_close(
        self, client, basic_user, board_with_writer, ticket_card
    ):
        last_list = board_with_writer.lists.order_by("order", "id").last()
        client.force_login(basic_user)

        with patch("aa_kanban.tasks.notify_ticket_thread.delay"):
            resp = client.post(
                reverse(
                    "aa_kanban:spa_api_move_card", kwargs={"card_id": ticket_card.id}
                ),
                json.dumps({"target_list_id": last_list.id, "new_position": 0}),
                content_type="application/json",
            )
        assert resp.status_code == 200
        assert resp.json()["prompt_close_thread"] is True

    def test_move_without_thread_never_prompts(
        self, client, basic_user, board_with_writer
    ):
        list_todo = board_with_writer.lists.get(name="To Do")
        card = Card.objects.create(list=list_todo, title="No thread card")
        last_list = board_with_writer.lists.order_by("order", "id").last()
        client.force_login(basic_user)

        resp = client.post(
            reverse("aa_kanban:spa_api_move_card", kwargs={"card_id": card.id}),
            json.dumps({"target_list_id": last_list.id, "new_position": 0}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["prompt_close_thread"] is False


@pytest.mark.django_db
class TestCloseCardThreadApi:
    """api_close_card_thread (SPA) mirrors the classic close_card_thread view."""

    @pytest.fixture
    def ticket_card(self, board_with_writer):
        list_todo = board_with_writer.lists.get(name="To Do")
        return Card.objects.create(
            list=list_todo,
            title="SPA Close Thread Card",
            discord_thread_id=555666777,
        )

    def test_close_card_thread_dispatches_task(self, client, basic_user, ticket_card):
        client.force_login(basic_user)
        with patch("aa_kanban.tasks.close_ticket_thread.delay") as mock_close:
            resp = client.post(
                reverse(
                    "aa_kanban:spa_api_close_card_thread",
                    kwargs={"card_id": ticket_card.id},
                )
            )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        mock_close.assert_called_once_with(555666777)

    def test_close_card_thread_requires_write_permission(
        self, client, other_user, ticket_card
    ):
        client.force_login(other_user)
        resp = client.post(
            reverse(
                "aa_kanban:spa_api_close_card_thread",
                kwargs={"card_id": ticket_card.id},
            )
        )
        assert resp.status_code == 403

    def test_close_card_thread_without_thread_returns_error(
        self, client, basic_user, board_with_writer
    ):
        list_todo = board_with_writer.lists.get(name="To Do")
        card = Card.objects.create(list=list_todo, title="No thread here")
        client.force_login(basic_user)

        resp = client.post(
            reverse("aa_kanban:spa_api_close_card_thread", kwargs={"card_id": card.id})
        )
        assert resp.status_code == 400
