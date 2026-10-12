"""Unit tests for stale card alert detection and Discord notifications (TASK-72)."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from aa_kanban.models import Board, Card, Comment, List
from aa_kanban.tasks import check_stale_cards


@pytest.fixture
def user_factory(db):
    """Create test users with basic_access permission."""
    _char_id = 9500

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
def board_setup(user_factory):
    """Set up a board with lists and a manager user."""
    manager = user_factory("stale_mgr", extra_perms=["aa_kanban.manage_boards"])
    board = Board.objects.create(
        name="Stale Test Board",
        slug="stale-test-board",
        stale_card_alert_hours=24,
        created_by=manager,
    )
    in_progress = board.lists.get(name="In Progress")
    done_list = board.lists.get(name="Done")
    afgerond_list = List.objects.create(board=board, name="Afgerond", order=10)

    return {
        "manager": manager,
        "board": board,
        "in_progress": in_progress,
        "done_list": done_list,
        "afgerond_list": afgerond_list,
    }


@pytest.mark.django_db
def test_stale_cards_disabled_when_hours_zero(board_setup):
    """If stale_card_alert_hours is 0, get_stale_cards returns an empty queryset."""
    board = board_setup["board"]
    board.stale_card_alert_hours = 0
    board.save(update_fields=["stale_card_alert_hours"])

    card = Card.objects.create(
        list=board_setup["in_progress"],
        title="Old Card",
    )
    # Manually backdate updated_at
    past_time = timezone.now() - timedelta(hours=48)
    Card.objects.filter(pk=card.pk).update(updated_at=past_time)

    assert board.get_stale_cards().count() == 0


@pytest.mark.django_db
def test_stale_cards_detection_and_column_exclusion(board_setup):
    """Stale cards are detected when inactive, and 'Done'/'Afgerond' columns are excluded."""
    board = board_setup["board"]
    now = timezone.now()
    past_48h = now - timedelta(hours=48)
    past_2h = now - timedelta(hours=2)

    # 1. Stale card in 'In Progress'
    card_stale = Card.objects.create(
        list=board_setup["in_progress"],
        title="Stale In Progress Card",
    )
    Card.objects.filter(pk=card_stale.pk).update(updated_at=past_48h)

    # 2. Fresh card in 'In Progress'
    card_fresh = Card.objects.create(
        list=board_setup["in_progress"],
        title="Fresh Card",
    )
    Card.objects.filter(pk=card_fresh.pk).update(updated_at=past_2h)

    # 3. Old card in 'Done' (must be excluded)
    card_done = Card.objects.create(
        list=board_setup["done_list"],
        title="Done Card",
    )
    Card.objects.filter(pk=card_done.pk).update(updated_at=past_48h)

    # 4. Old card in 'Afgerond' (must be excluded)
    card_afgerond = Card.objects.create(
        list=board_setup["afgerond_list"],
        title="Afgerond Card",
    )
    Card.objects.filter(pk=card_afgerond.pk).update(updated_at=past_48h)

    stale_cards = list(board.get_stale_cards())
    assert card_stale in stale_cards
    assert card_fresh not in stale_cards
    assert card_done not in stale_cards
    assert card_afgerond not in stale_cards


@pytest.mark.django_db
def test_stale_cards_recent_comment_prevents_alert(board_setup):
    """A recent comment counts as activity and prevents a card from being marked as stale."""
    board = board_setup["board"]
    manager = board_setup["manager"]
    now = timezone.now()
    past_48h = now - timedelta(hours=48)

    card = Card.objects.create(
        list=board_setup["in_progress"],
        title="Card with Recent Comment",
    )
    Card.objects.filter(pk=card.pk).update(updated_at=past_48h)

    # Add a comment created 1 hour ago
    Comment.objects.create(
        card=card,
        author=manager,
        text="Recent update on this card",
    )

    stale_cards = list(board.get_stale_cards())
    assert card not in stale_cards


@pytest.mark.django_db
def test_create_and_edit_board_with_stale_alert_fields(user_factory):
    """Board create and edit forms correctly parse and save stale alert settings."""
    manager = user_factory("mgr_form", extra_perms=["aa_kanban.manage_boards"])
    client = Client()
    client.force_login(manager)

    # Create board
    response = client.post(
        reverse("aa_kanban:create_board"),
        {
            "name": "Alerts Board",
            "description": "Board with alerts",
            "stale_card_alert_hours": "36",
            "stale_card_repeat_hours": "12",
            "discord_alert_channel_id": "987654321",
            "discord_alert_webhook": "https://discord.com/api/webhooks/alert-test",
            "discord_webhook_cards": "https://discord.com/api/webhooks/cards-test",
        },
    )
    assert response.status_code in [200, 204, 302]

    board = Board.objects.get(name="Alerts Board")
    assert board.stale_card_alert_hours == 36
    assert board.stale_card_repeat_hours == 12
    assert board.discord_alert_channel_id == 987654321
    assert board.discord_alert_webhook == "https://discord.com/api/webhooks/alert-test"
    assert board.discord_webhook_cards == "https://discord.com/api/webhooks/cards-test"

    # Edit board
    response = client.post(
        reverse("aa_kanban:edit_board", kwargs={"board_slug": board.slug}),
        {
            "name": "Alerts Board Updated",
            "description": "Updated",
            "stale_card_alert_hours": "72",
            "stale_card_repeat_hours": "48",
            "discord_alert_channel_id": "111222333",
            "discord_alert_webhook": "",
            "discord_webhook_cards": "https://discord.com/api/webhooks/cards-test",
        },
    )
    assert response.status_code in [200, 204, 302]

    board.refresh_from_db()
    assert board.name == "Alerts Board Updated"
    assert board.stale_card_alert_hours == 72
    assert board.stale_card_repeat_hours == 48
    assert board.discord_alert_channel_id == 111222333
    assert board.discord_alert_webhook is None


@pytest.mark.django_db
def test_check_stale_cards_task_webhook_dispatch(board_setup):
    """Celery task check_stale_cards sends a formatted Discord webhook notification."""
    board = board_setup["board"]
    board.discord_alert_webhook = "https://discord.com/api/webhooks/stale-alert"
    board.save(update_fields=["discord_alert_webhook"])

    past_48h = timezone.now() - timedelta(hours=48)
    card = Card.objects.create(
        list=board_setup["in_progress"],
        title="Delayed Task 1",
    )
    Card.objects.filter(pk=card.pk).update(updated_at=past_48h)

    with patch("aa_kanban.utils.send_discord_webhook") as mock_webhook:
        check_stale_cards()
        assert mock_webhook.called
        args, _ = mock_webhook.call_args
        assert args[0] == "https://discord.com/api/webhooks/stale-alert"
        assert "Delayed Task 1" in args[1]
        assert "Stale Test Board" in args[1]
        card.refresh_from_db()
        assert card.last_stale_alert_at is not None


@pytest.mark.django_db
def test_check_stale_cards_task_bot_channel_dispatch(board_setup):
    """Celery task check_stale_cards delegates to aadiscordbot if channel_id is set."""
    board = board_setup["board"]
    board.discord_alert_channel_id = 9988776655
    board.save(update_fields=["discord_alert_channel_id"])

    past_48h = timezone.now() - timedelta(hours=48)
    card = Card.objects.create(
        list=board_setup["in_progress"],
        title="Stuck in Review",
    )
    Card.objects.filter(pk=card.pk).update(updated_at=past_48h)

    mock_run_task = MagicMock()
    with patch.dict(
        "sys.modules",
        {"aadiscordbot.tasks": MagicMock(run_task_function=mock_run_task)},
    ):
        check_stale_cards()
        assert mock_run_task.apply_async.called
        kwargs = mock_run_task.apply_async.call_args[1]
        assert kwargs["queue"] == "aadiscordbot"
        assert kwargs["kwargs"]["task_args"][0] == 9988776655
        assert "Stuck in Review" in kwargs["kwargs"]["task_args"][1]


@pytest.mark.django_db
def test_format_stale_cards_message_english_and_dutch(board_setup):
    """Test format_stale_cards_message outputs English by default and translates to Dutch."""
    from django.utils import translation

    from aa_kanban.tasks import format_stale_cards_message

    board = board_setup["board"]
    card = Card.objects.create(
        list=board_setup["in_progress"],
        title="Stale Unit Card",
    )
    stale_cards = [card]

    # 1. English (default)
    with translation.override("en"):
        msg_en = format_stale_cards_message(board, stale_cards)
        assert "Kanban Alert: Stale Cards" in msg_en
        assert "There are **1** card(s) that have been inactive for more than" in msg_en
        assert "List: `In Progress`" in msg_en
        assert "Inactive:" in msg_en
        assert "Assigned: Unassigned" in msg_en
        assert "View Board" in msg_en

    # 2. Dutch
    with translation.override("nl"):
        msg_nl = format_stale_cards_message(board, stale_cards)
        assert "Kanban Signalering: Stilstaande Cards" in msg_nl
        assert "Er zijn **1** card(s) die langer dan" in msg_nl
        assert "Lijst: `In Progress`" in msg_nl
        assert "Stilstand:" in msg_nl
        assert "Toegewezen: Niet toegewezen" in msg_nl
        assert "Bord bekijken" in msg_nl


@pytest.mark.django_db
def test_stale_cards_throttling_within_repeat_interval(board_setup):
    """Cards that were alerted recently are excluded from subsequent checks within repeat_hours."""
    board = board_setup["board"]
    board.stale_card_alert_hours = 24
    board.stale_card_repeat_hours = 24
    board.save(update_fields=["stale_card_alert_hours", "stale_card_repeat_hours"])

    past_48h = timezone.now() - timedelta(hours=48)
    alerted_2h_ago = timezone.now() - timedelta(hours=2)

    card = Card.objects.create(
        list=board_setup["in_progress"],
        title="Throttled Card",
    )
    Card.objects.filter(pk=card.pk).update(
        updated_at=past_48h,
        last_stale_alert_at=alerted_2h_ago,
    )

    # 48h inactive, but alerted 2h ago and repeat is 24h -> should be throttled
    stale_cards = list(board.get_stale_cards())
    assert card not in stale_cards


@pytest.mark.django_db
def test_stale_cards_repeat_after_interval_passed(board_setup):
    """Cards are alerted again once stale_card_repeat_hours have elapsed since last_stale_alert_at."""
    board = board_setup["board"]
    board.stale_card_alert_hours = 24
    board.stale_card_repeat_hours = 24
    board.save(update_fields=["stale_card_alert_hours", "stale_card_repeat_hours"])

    past_72h = timezone.now() - timedelta(hours=72)
    alerted_25h_ago = timezone.now() - timedelta(hours=25)

    card = Card.objects.create(
        list=board_setup["in_progress"],
        title="Repeat Alert Card",
    )
    Card.objects.filter(pk=card.pk).update(
        updated_at=past_72h,
        last_stale_alert_at=alerted_25h_ago,
    )

    # 72h inactive, alerted 25h ago, repeat is 24h -> should be included for repeat alert
    stale_cards = list(board.get_stale_cards())
    assert card in stale_cards


@pytest.mark.django_db
def test_stale_cards_one_time_alert_policy(board_setup):
    """When stale_card_repeat_hours is 0, cards are only alerted once until new activity occurs."""
    board = board_setup["board"]
    board.stale_card_alert_hours = 24
    board.stale_card_repeat_hours = 0
    board.save(update_fields=["stale_card_alert_hours", "stale_card_repeat_hours"])

    past_48h = timezone.now() - timedelta(hours=48)

    card = Card.objects.create(
        list=board_setup["in_progress"],
        title="One Time Alert Card",
    )
    Card.objects.filter(pk=card.pk).update(updated_at=past_48h)

    # First check: never alerted before -> included
    assert card in list(board.get_stale_cards())

    # Simulate alert sent
    Card.objects.filter(pk=card.pk).update(last_stale_alert_at=timezone.now())

    # Second check: already alerted, repeat is 0 -> excluded
    assert card not in list(board.get_stale_cards())

    # If new activity occurs (e.g. card title/comment updated) and then becomes stale again
    past_30h = timezone.now() - timedelta(hours=30)
    old_alert = timezone.now() - timedelta(hours=35)
    Card.objects.filter(pk=card.pk).update(
        updated_at=past_30h,
        last_stale_alert_at=old_alert,
    )
    # New activity happened after the old alert (30h ago vs 35h ago) -> included again!
    assert card in list(board.get_stale_cards())
