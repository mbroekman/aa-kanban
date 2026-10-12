"""Tests for Discord ticket thread notifications on card move, label change, and team change (TASK-73)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse

from aa_kanban.models import Board, Card, KanbanGroup, KanbanTeam, Label
from aa_kanban.services import move_kanban_card
from aa_kanban.tasks import (
    _create_discord_thread,
    _send_discord_thread_message,
    notify_ticket_thread,
)


@pytest.fixture
def user_factory(db):
    """Create test users with basic_access permission."""
    _char_id = 9600

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
def ticket_setup(user_factory):
    """Set up a board with lists, teams, labels, and a user with write access."""
    manager = user_factory("thread_mgr", extra_perms=["aa_kanban.manage_boards"])
    writer = user_factory("thread_writer")
    write_grp = KanbanGroup.objects.create(name="Thread Writers")
    writer.kanban_groups.add(write_grp)

    board = Board.objects.create(
        name="Ticket Thread Board",
        slug="ticket-thread-board",
        created_by=manager,
    )
    board.write_groups.add(write_grp)

    list_todo = board.lists.get(name="To Do")
    list_in_progress = board.lists.get(name="In Progress")

    label = Label.objects.create(name="Bug", color="danger")
    team = KanbanTeam.objects.create(
        name="Dev Ops",
        discord_role_id=123456789,
    )

    card = Card.objects.create(
        list=list_todo,
        title="Ticket with Thread",
        discord_thread_id=555666777,
        created_by=manager,
    )

    return {
        "manager": manager,
        "writer": writer,
        "board": board,
        "list_todo": list_todo,
        "list_in_progress": list_in_progress,
        "label": label,
        "team": team,
        "card": card,
    }


@pytest.mark.django_db
def test_move_card_notifies_thread(ticket_setup):
    """Moving a ticket card between columns sends a notification to its Discord thread."""
    card = ticket_setup["card"]
    target_list = ticket_setup["list_in_progress"]
    writer = ticket_setup["writer"]

    client = Client()
    client.force_login(writer)

    with patch("aa_kanban.tasks.notify_ticket_thread.delay") as mock_notify:
        response = client.post(
            reverse("aa_kanban:move_card", kwargs={"card_id": card.id}),
            {
                "target_list_id": target_list.id,
                "new_position": 0,
            },
        )
        assert response.status_code == 200
        assert mock_notify.called
        args, _ = mock_notify.call_args
        assert args[0] == 555666777
        assert "To Do" in args[1]
        assert "In Progress" in args[1]
        assert writer.username in args[1]


@pytest.mark.django_db
def test_toggle_label_notifies_thread(ticket_setup):
    """Adding and removing a label sends update messages to the ticket's Discord thread."""
    card = ticket_setup["card"]
    label = ticket_setup["label"]
    writer = ticket_setup["writer"]

    client = Client()
    client.force_login(writer)

    # 1. Add label
    with patch("aa_kanban.tasks.notify_ticket_thread.delay") as mock_notify:
        response = client.post(
            reverse("aa_kanban:toggle_label", kwargs={"card_id": card.id}),
            {"label_id": label.id},
        )
        assert response.status_code == 200
        assert mock_notify.called
        args, _ = mock_notify.call_args
        assert args[0] == 555666777
        assert "Label Added" in args[1] or "Label Toegevoegd" in args[1]
        assert "Bug" in args[1]

    # 2. Remove label
    with patch("aa_kanban.tasks.notify_ticket_thread.delay") as mock_notify:
        response = client.post(
            reverse("aa_kanban:toggle_label", kwargs={"card_id": card.id}),
            {"label_id": label.id},
        )
        assert response.status_code == 200
        assert mock_notify.called
        args, _ = mock_notify.call_args
        assert args[0] == 555666777
        assert "Label Removed" in args[1] or "Label Verwijderd" in args[1]
        assert "Bug" in args[1]


@pytest.mark.django_db
def test_update_card_team_notifies_thread(ticket_setup):
    """Assigning or clearing a team sends an update message and auto-invites team members."""
    card = ticket_setup["card"]
    team = ticket_setup["team"]
    writer = ticket_setup["writer"]

    client = Client()
    client.force_login(writer)

    # 1. Assign team
    with patch("aa_kanban.tasks.notify_ticket_thread.delay") as mock_notify:
        response = client.post(
            reverse("aa_kanban:update_card_team", kwargs={"card_id": card.id}),
            {"team_id": team.id},
        )
        assert response.status_code == 200
        assert mock_notify.called
        args, kwargs = mock_notify.call_args
        assert args[0] == 555666777
        assert "Dev Ops" in args[1]
        assert "123456789" in args[1]  # role mention
        assert kwargs.get("team_id") == team.id

    # 2. Unassign team
    with patch("aa_kanban.tasks.notify_ticket_thread.delay") as mock_notify:
        response = client.post(
            reverse("aa_kanban:update_card_team", kwargs={"card_id": card.id}),
            {"team_id": ""},
        )
        assert response.status_code == 200
        assert mock_notify.called
        args, _ = mock_notify.call_args
        assert args[0] == 555666777
        assert "unassigned" in args[1] or "verwijderd" in args[1]


@pytest.mark.django_db
def test_services_move_kanban_card_notifies_thread(ticket_setup):
    """services.move_kanban_card notifies thread if card has discord_thread_id."""
    card = ticket_setup["card"]

    with patch("aa_kanban.tasks.notify_ticket_thread.delay") as mock_notify:
        move_kanban_card(card.id, "In Progress")
        assert mock_notify.called
        args, _ = mock_notify.call_args
        assert args[0] == 555666777
        assert "To Do" in args[1]
        assert "In Progress" in args[1]


@pytest.mark.django_db
def test_notify_ticket_thread_delegates_to_aadiscordbot():
    """notify_ticket_thread dispatches to aadiscordbot queue."""
    mock_run_task = MagicMock()
    with patch.dict(
        "sys.modules",
        {"aadiscordbot.tasks": MagicMock(run_task_function=mock_run_task)},
    ):
        notify_ticket_thread(555666777, "Test Message", team_id=42)
        assert mock_run_task.apply_async.called
        kwargs = mock_run_task.apply_async.call_args[1]
        assert kwargs["queue"] == "aadiscordbot"
        assert kwargs["kwargs"]["task_args"] == [555666777, "Test Message"]
        assert kwargs["kwargs"]["task_kwargs"] == {"team_id": 42}


@pytest.mark.django_db
def test_add_and_remove_authgroup_to_team(ticket_setup):
    """HTMX endpoints add and remove Auth Groups from a KanbanTeam."""
    manager = ticket_setup["manager"]
    team = ticket_setup["team"]
    auth_grp = Group.objects.create(name="Fleet Commanders")

    client = Client()
    client.force_login(manager)

    # 1. Add Auth Group
    add_url = reverse("aa_kanban:add_authgroup_to_team", kwargs={"team_id": team.id})
    resp = client.post(add_url, {"authgroup_id": auth_grp.id})
    assert resp.status_code == 200
    assert auth_grp in team.groups.all()
    assert "Fleet Commanders" in resp.content.decode()

    # 2. Remove Auth Group
    remove_url = reverse(
        "aa_kanban:remove_authgroup_from_team",
        kwargs={"team_id": team.id, "authgroup_id": auth_grp.id},
    )
    resp = client.post(remove_url)
    assert resp.status_code == 200
    assert auth_grp not in team.groups.all()


@pytest.mark.django_db(transaction=True)
def test_create_discord_thread_auto_invites_auth_group_members(user_factory):
    """_create_discord_thread auto-invites both direct team members and users from linked auth groups."""
    import asyncio

    mgr = user_factory("mgr_thread", extra_perms=["aa_kanban.manage_boards"])
    u1 = user_factory("direct_member")
    u2 = user_factory("group_member")

    auth_grp = Group.objects.create(name="Support Wing")
    u2.groups.add(auth_grp)

    board = Board.objects.create(
        name="Tickets Board",
        slug="tickets-board",
        discord_ticket_channel_id=987654321,
        created_by=mgr,
    )
    lst = board.lists.get(name="To Do")
    team = KanbanTeam.objects.create(name="Support Team")
    team.members.add(u1)
    team.groups.add(auth_grp)

    card = Card.objects.create(
        list=lst,
        title="Support Request #1",
        assigned_team=team,
        created_by=mgr,
    )

    # Mock Discord bot
    mock_thread = AsyncMock()
    mock_thread.id = 888999
    mock_channel = AsyncMock()
    mock_channel.create_thread = AsyncMock(return_value=mock_thread)
    mock_bot = MagicMock()
    mock_bot.get_channel.return_value = mock_channel

    mock_du1 = MagicMock(uid=111222)
    mock_du2 = MagicMock(uid=333444)

    mock_discord = MagicMock()
    mock_discord.Object = lambda id: MagicMock(id=id)
    mock_discord.ChannelType = MagicMock(private_thread="private_thread")

    with (
        patch.dict("sys.modules", {"discord": mock_discord}),
        patch(
            "allianceauth.services.modules.discord.models.DiscordUser.objects.filter",
            return_value=[mock_du1, mock_du2],
        ) as mock_filter,
    ):
        asyncio.run(_create_discord_thread(mock_bot, card.id))

        card.refresh_from_db()
        assert card.discord_thread_id == 888999

        # Thread must be created as private, directly on the channel (not
        # from a public starter message, which can only ever be public).
        mock_channel.create_thread.assert_called_once()
        create_kwargs = mock_channel.create_thread.call_args.kwargs
        assert create_kwargs["type"] == "private_thread"
        assert create_kwargs["invitable"] is False
        mock_channel.send.assert_not_called()
        mock_thread.send.assert_called_once()

        assert mock_filter.called
        users_passed = set(mock_filter.call_args[1]["user__in"])
        assert users_passed == {u1, u2}

        # Verify both direct and auth group users were invited
        assert mock_thread.add_user.call_count == 2
        invited_uids = {call.args[0].id for call in mock_thread.add_user.call_args_list}
        assert invited_uids == {111222, 333444}


@pytest.mark.django_db(transaction=True)
def test_create_discord_thread_invites_ticket_creator(user_factory):
    """_create_discord_thread creates a private thread and invites the creator."""
    import asyncio

    creator = user_factory("ticket_creator")

    board = Board.objects.create(
        name="Creator Invite Board",
        slug="creator-invite-board",
        discord_ticket_channel_id=555666777,
        created_by=creator,
    )
    lst = board.lists.get(name="To Do")
    card = Card.objects.create(
        list=lst,
        title="Creator Invite Ticket",
        created_by=creator,
    )

    mock_thread = AsyncMock()
    mock_thread.id = 111000
    mock_channel = AsyncMock()
    mock_channel.create_thread = AsyncMock(return_value=mock_thread)
    mock_bot = MagicMock()
    mock_bot.get_channel.return_value = mock_channel

    mock_creator_du = MagicMock(uid=424242)
    mock_queryset = MagicMock()
    mock_queryset.first = lambda: mock_creator_du

    mock_discord = MagicMock()
    mock_discord.Object = lambda id: MagicMock(id=id)
    mock_discord.ChannelType = MagicMock(private_thread="private_thread")

    with (
        patch.dict("sys.modules", {"discord": mock_discord}),
        patch(
            "allianceauth.services.modules.discord.models.DiscordUser.objects.filter",
            return_value=mock_queryset,
        ),
    ):
        asyncio.run(_create_discord_thread(mock_bot, card.id))

        card.refresh_from_db()
        assert card.discord_thread_id == 111000

        create_kwargs = mock_channel.create_thread.call_args.kwargs
        assert create_kwargs["type"] == "private_thread"

        mock_thread.add_user.assert_called_once()
        assert mock_thread.add_user.call_args.args[0].id == 424242


@pytest.mark.django_db(transaction=True)
def test_send_discord_thread_message_auto_invites_auth_group_members(user_factory):
    """_send_discord_thread_message auto-invites both direct and group members when team_id is provided."""
    import asyncio

    u1 = user_factory("msg_direct_member")
    u2 = user_factory("msg_group_member")

    auth_grp = Group.objects.create(name="Strike Wing")
    u2.groups.add(auth_grp)

    team = KanbanTeam.objects.create(name="Strike Team Ops")
    team.members.add(u1)
    team.groups.add(auth_grp)

    mock_thread = AsyncMock()
    mock_bot = MagicMock()
    mock_bot.get_channel.return_value = mock_thread

    mock_du1 = MagicMock(uid=555111)
    mock_du2 = MagicMock(uid=555222)

    mock_discord = MagicMock()
    mock_discord.Object = lambda id: MagicMock(id=id)

    with (
        patch.dict("sys.modules", {"discord": mock_discord}),
        patch(
            "allianceauth.services.modules.discord.models.DiscordUser.objects.filter",
            return_value=[mock_du1, mock_du2],
        ) as mock_filter,
    ):
        asyncio.run(
            _send_discord_thread_message(
                mock_bot,
                thread_id=777888,
                message_content="Team assigned",
                team_id=team.id,
            )
        )

        mock_thread.send.assert_called_once_with(content="Team assigned")
        assert mock_filter.called
        users_passed = set(mock_filter.call_args[1]["user__in"])
        assert users_passed == {u1, u2}

        assert mock_thread.add_user.call_count == 2
        invited_uids = {call.args[0].id for call in mock_thread.add_user.call_args_list}
        assert invited_uids == {555111, 555222}


@pytest.mark.django_db
def test_edit_kanban_team_modal_get_and_post(ticket_setup):
    """edit_kanban_team GET returns modal HTML, POST updates team and triggers closeModal."""
    manager = ticket_setup["manager"]
    team = ticket_setup["team"]
    board = ticket_setup["board"]
    board.is_ticket_board = True
    board.save()

    client = Client()
    client.force_login(manager)

    # 1. GET returns edit modal with form fields
    edit_url = reverse("aa_kanban:edit_kanban_team", kwargs={"team_id": team.id})
    resp_get = client.get(edit_url)
    assert resp_get.status_code == 200
    assert "modal-header" in resp_get.content.decode()
    assert "Edit Team:" in resp_get.content.decode()
    assert team.name in resp_get.content.decode()
    assert board.name in resp_get.content.decode()

    # 2. POST updates team
    resp_post = client.post(
        edit_url,
        {
            "name": "Dev Ops Updated",
            "discord_role_id": "987654321",
            "ticket_board_id": str(board.id),
        },
    )
    assert resp_post.status_code == 200
    assert resp_post.headers.get("HX-Trigger") == "closeModal"
    team.refresh_from_db()
    assert team.name == "Dev Ops Updated"
    assert team.discord_role_id == 987654321
    assert team.ticket_board_id == board.id
