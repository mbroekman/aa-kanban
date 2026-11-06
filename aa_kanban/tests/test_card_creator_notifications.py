"""Tests for Discord DM notifications sent to a card's creator on card changes.

Covers the rule that the creator is DM'd when their card changes, except when
they made the change themselves, or are already an assignee or member of the
card's assigned team (in which case they are informed through those existing
channels and must not be notified twice).
"""

from unittest.mock import MagicMock, patch

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.test import Client
from django.urls import reverse

from aa_kanban.models import Board, Card, KanbanGroup, KanbanTeam, Label
from aa_kanban.services import move_kanban_card
from aa_kanban.tasks import notify_card_creator


@pytest.fixture
def user_factory(db):
    """Create test users with basic_access permission."""
    _char_id = 9800

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
def creator_setup(user_factory):
    """Board with a card whose creator is distinct from the acting writer."""
    creator = user_factory("card_creator")
    writer = user_factory("other_writer")
    write_grp = KanbanGroup.objects.create(name="Creator Notif Writers")
    writer.kanban_groups.add(write_grp)
    creator.kanban_groups.add(write_grp)

    board = Board.objects.create(
        name="Creator Notif Board",
        slug="creator-notif-board",
        created_by=creator,
    )
    board.write_groups.add(write_grp)

    list_todo = board.lists.get(name="To Do")
    list_in_progress = board.lists.get(name="In Progress")
    label = Label.objects.create(name="Urgent", color="danger")
    team = KanbanTeam.objects.create(name="Ops Team")

    card = Card.objects.create(
        list=list_todo,
        title="Creator Notif Card",
        created_by=creator,
    )

    return {
        "creator": creator,
        "writer": writer,
        "board": board,
        "list_todo": list_todo,
        "list_in_progress": list_in_progress,
        "label": label,
        "team": team,
        "card": card,
    }


@pytest.mark.django_db
def test_move_card_notifies_creator(creator_setup):
    """Moving a card DMs its creator when someone else moved it."""
    data = creator_setup
    card = data["card"]
    creator = data["creator"]
    writer = data["writer"]

    client = Client()
    client.force_login(writer)

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        response = client.post(
            reverse("aa_kanban:move_card", kwargs={"card_id": card.id}),
            {"target_list_id": data["list_in_progress"].id, "new_position": 0},
        )
        assert response.status_code == 200
        mock_tasks.send_direct_message_by_user_id.delay.assert_called_once()
        args = mock_tasks.send_direct_message_by_user_id.delay.call_args.args
        assert args[0] == creator.id
        assert "Creator Notif Card" in args[1]
        assert writer.username in args[1]


@pytest.mark.django_db
def test_move_card_by_creator_does_not_self_notify(creator_setup):
    """A card's creator moving their own card does not DM themselves."""
    data = creator_setup
    card = data["card"]
    creator = data["creator"]

    client = Client()
    client.force_login(creator)

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        response = client.post(
            reverse("aa_kanban:move_card", kwargs={"card_id": card.id}),
            {"target_list_id": data["list_in_progress"].id, "new_position": 0},
        )
        assert response.status_code == 200
        mock_tasks.send_direct_message_by_user_id.delay.assert_not_called()


@pytest.mark.django_db
def test_move_card_skips_creator_dm_when_creator_is_assignee(creator_setup):
    """No creator DM is sent when the creator is already an assignee on the card."""
    data = creator_setup
    card = data["card"]
    creator = data["creator"]
    writer = data["writer"]
    card.assignees.add(creator)

    client = Client()
    client.force_login(writer)

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        response = client.post(
            reverse("aa_kanban:move_card", kwargs={"card_id": card.id}),
            {"target_list_id": data["list_in_progress"].id, "new_position": 0},
        )
        assert response.status_code == 200
        mock_tasks.send_direct_message_by_user_id.delay.assert_not_called()


@pytest.mark.django_db
def test_move_card_skips_creator_dm_when_creator_in_assigned_team(creator_setup):
    """No creator DM when the creator is a member of the card's assigned team."""
    data = creator_setup
    card = data["card"]
    creator = data["creator"]
    writer = data["writer"]
    team = data["team"]
    team.members.add(creator)
    card.assigned_team = team
    card.save(update_fields=["assigned_team"])

    client = Client()
    client.force_login(writer)

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        response = client.post(
            reverse("aa_kanban:move_card", kwargs={"card_id": card.id}),
            {"target_list_id": data["list_in_progress"].id, "new_position": 0},
        )
        assert response.status_code == 200
        mock_tasks.send_direct_message_by_user_id.delay.assert_not_called()


@pytest.mark.django_db
def test_add_comment_notifies_creator(creator_setup):
    """Commenting on a card DMs its creator when someone else wrote the comment."""
    data = creator_setup
    card = data["card"]
    creator = data["creator"]
    writer = data["writer"]

    client = Client()
    client.force_login(writer)

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        response = client.post(
            reverse("aa_kanban:add_comment", kwargs={"card_id": card.id}),
            {"comment": "Any update on this?"},
        )
        assert response.status_code == 200
        mock_tasks.send_direct_message_by_user_id.delay.assert_called_once()
        args = mock_tasks.send_direct_message_by_user_id.delay.call_args.args
        assert args[0] == creator.id
        assert writer.username in args[1]
        assert "Creator Notif Card" in args[1]


@pytest.mark.django_db
def test_toggle_label_notifies_creator(creator_setup):
    """Adding a label to a card DMs its creator."""
    data = creator_setup
    card = data["card"]
    creator = data["creator"]
    writer = data["writer"]
    label = data["label"]

    client = Client()
    client.force_login(writer)

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        response = client.post(
            reverse("aa_kanban:toggle_label", kwargs={"card_id": card.id}),
            {"label_id": label.id},
        )
        assert response.status_code == 200
        mock_tasks.send_direct_message_by_user_id.delay.assert_called_once()
        args = mock_tasks.send_direct_message_by_user_id.delay.call_args.args
        assert args[0] == creator.id
        assert "Urgent" in args[1]


@pytest.mark.django_db
def test_update_card_team_notifies_creator_unless_member(creator_setup):
    """Assigning a team DMs the creator unless they belong to that team."""
    data = creator_setup
    card = data["card"]
    creator = data["creator"]
    writer = data["writer"]
    team = data["team"]

    client = Client()
    client.force_login(writer)

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        response = client.post(
            reverse("aa_kanban:update_card_team", kwargs={"card_id": card.id}),
            {"team_id": team.id},
        )
        assert response.status_code == 200
        mock_tasks.send_direct_message_by_user_id.delay.assert_called_once()
        args = mock_tasks.send_direct_message_by_user_id.delay.call_args.args
        assert args[0] == creator.id
        assert "Ops Team" in args[1]

    # Now make the creator a member of that same team: reassigning it (still
    # a change, team was briefly unset above) must not DM the creator since
    # they are themselves on the team.
    team.members.add(creator)
    card.assigned_team = None
    card.save(update_fields=["assigned_team"])
    mock_tasks.reset_mock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        response = client.post(
            reverse("aa_kanban:update_card_team", kwargs={"card_id": card.id}),
            {"team_id": team.id},
        )
        assert response.status_code == 200
        mock_tasks.send_direct_message_by_user_id.delay.assert_not_called()


@pytest.mark.django_db
def test_services_move_kanban_card_notifies_creator(creator_setup):
    """services.move_kanban_card DMs the card's creator (no acting user to exclude)."""
    data = creator_setup
    card = data["card"]
    creator = data["creator"]

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        move_kanban_card(card.id, "In Progress")
        mock_tasks.send_direct_message_by_user_id.delay.assert_called_once()
        args = mock_tasks.send_direct_message_by_user_id.delay.call_args.args
        assert args[0] == creator.id


@pytest.mark.django_db
def test_notify_card_creator_skips_when_no_creator():
    """notify_card_creator is a no-op when the card has no recorded creator."""
    board = Board.objects.create(name="No Creator Board", slug="no-creator-board")
    list_todo = board.lists.get(name="To Do")
    card = Card.objects.create(list=list_todo, title="Orphan Card", created_by=None)

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        notify_card_creator(card, "irrelevant message")
        mock_tasks.send_direct_message_by_user_id.delay.assert_not_called()


@pytest.mark.django_db
def test_card_with_ticket_thread_skips_dm_unless_thread_misses_it(creator_setup):
    """The creator is in the ticket thread: no DM for changes posted there, a DM for the rest."""
    card = creator_setup["card"]
    card.discord_thread_id = 1234
    card.save(update_fields=["discord_thread_id"])
    writer = creator_setup["writer"]

    mock_tasks = MagicMock()
    with patch.dict("sys.modules", {"aadiscordbot.tasks": mock_tasks}):
        notify_card_creator(card, "moved", actor=writer)
        mock_tasks.send_direct_message_by_user_id.delay.assert_not_called()

        notify_card_creator(card, "commented", actor=writer, posted_in_thread=False)
        mock_tasks.send_direct_message_by_user_id.delay.assert_called_once_with(
            creator_setup["creator"].id, "commented"
        )
