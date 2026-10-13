"""Unit tests for per-board auto-archiving of cards in the last list (TASK-95)."""

from datetime import timedelta

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from aa_kanban.models import Board, Card, KanbanGroup
from aa_kanban.services import move_kanban_card
from aa_kanban.tasks import archive_done_cards


@pytest.fixture
def user_factory(db):
    """Create test users with basic_access permission."""
    _char_id = 9700

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
    """Set up a board with the default lists and a write-access user."""
    manager = user_factory("archive_mgr", extra_perms=["aa_kanban.manage_boards"])
    write_grp = KanbanGroup.objects.create(name="Archive Writers")
    writer = user_factory("archive_writer")
    writer.kanban_groups.add(write_grp)

    board = Board.objects.create(
        name="Archive Test Board",
        slug="archive-test-board",
        archive_after_days=7,
        created_by=manager,
    )
    board.write_groups.add(write_grp)

    in_progress = board.lists.get(name="In Progress")
    done_list = board.lists.order_by("order", "id").last()

    return {
        "manager": manager,
        "writer": writer,
        "board": board,
        "in_progress": in_progress,
        "done_list": done_list,
    }


@pytest.mark.django_db
def test_move_card_sets_moved_to_list_at(board_setup):
    """Moving a card to a different list updates moved_to_list_at."""
    card = Card.objects.create(list=board_setup["in_progress"], title="Task")
    assert card.moved_to_list_at is None

    client = Client()
    client.force_login(board_setup["writer"])
    response = client.post(
        reverse("aa_kanban:move_card", kwargs={"card_id": card.id}),
        {"target_list_id": board_setup["done_list"].id, "new_position": 0},
    )
    assert response.status_code == 200

    card.refresh_from_db()
    assert card.moved_to_list_at is not None


@pytest.mark.django_db
def test_move_card_same_list_reorder_does_not_touch_moved_to_list_at(board_setup):
    """Reordering within the same list does not update moved_to_list_at."""
    card1 = Card.objects.create(
        list=board_setup["in_progress"], title="A", order=0
    )
    Card.objects.create(list=board_setup["in_progress"], title="B", order=1)

    original_time = timezone.now() - timedelta(days=3)
    Card.objects.filter(pk=card1.pk).update(moved_to_list_at=original_time)

    client = Client()
    client.force_login(board_setup["writer"])
    response = client.post(
        reverse("aa_kanban:move_card", kwargs={"card_id": card1.id}),
        {"target_list_id": board_setup["in_progress"].id, "new_position": 1},
    )
    assert response.status_code == 200

    card1.refresh_from_db()
    assert card1.moved_to_list_at == original_time


@pytest.mark.django_db
def test_services_move_kanban_card_sets_moved_to_list_at(board_setup):
    """services.move_kanban_card also updates moved_to_list_at on a list change."""
    card = Card.objects.create(list=board_setup["in_progress"], title="Ticket")
    move_kanban_card(card.id, board_setup["done_list"].name)

    card.refresh_from_db()
    assert card.moved_to_list_at is not None


@pytest.mark.django_db
def test_archive_done_cards_archives_old_cards_in_last_list(board_setup):
    """Cards past archive_after_days in the last list get archived."""
    card = Card.objects.create(list=board_setup["done_list"], title="Finished")
    old_time = timezone.now() - timedelta(days=10)
    Card.objects.filter(pk=card.pk).update(moved_to_list_at=old_time)

    archive_done_cards()

    card.refresh_from_db()
    assert card.is_archived is True
    assert card.archived_at is not None


@pytest.mark.django_db
def test_archive_done_cards_leaves_recent_cards_alone(board_setup):
    """Cards still within the archive_after_days window are not archived."""
    card = Card.objects.create(list=board_setup["done_list"], title="Just finished")
    recent_time = timezone.now() - timedelta(days=1)
    Card.objects.filter(pk=card.pk).update(moved_to_list_at=recent_time)

    archive_done_cards()

    card.refresh_from_db()
    assert card.is_archived is False


@pytest.mark.django_db
def test_archive_done_cards_ignores_non_last_list(board_setup):
    """A card sitting long in a non-last list is never auto-archived."""
    card = Card.objects.create(list=board_setup["in_progress"], title="Stuck")
    old_time = timezone.now() - timedelta(days=30)
    Card.objects.filter(pk=card.pk).update(moved_to_list_at=old_time)

    archive_done_cards()

    card.refresh_from_db()
    assert card.is_archived is False


@pytest.mark.django_db
def test_archive_done_cards_disabled_when_archive_after_days_zero(board_setup):
    """Boards with archive_after_days=0 are skipped entirely."""
    board = board_setup["board"]
    board.archive_after_days = 0
    board.save(update_fields=["archive_after_days"])

    card = Card.objects.create(list=board_setup["done_list"], title="Finished")
    old_time = timezone.now() - timedelta(days=100)
    Card.objects.filter(pk=card.pk).update(moved_to_list_at=old_time)

    archive_done_cards()

    card.refresh_from_db()
    assert card.is_archived is False


@pytest.mark.django_db
def test_archive_done_cards_falls_back_to_created_at(board_setup):
    """Cards created directly in the last list (no moved_to_list_at) use created_at."""
    card = Card.objects.create(list=board_setup["done_list"], title="Born done")
    old_time = timezone.now() - timedelta(days=10)
    Card.objects.filter(pk=card.pk).update(created_at=old_time)
    assert card.moved_to_list_at is None

    archive_done_cards()

    card.refresh_from_db()
    assert card.is_archived is True


@pytest.mark.django_db
def test_board_detail_excludes_archived_cards(board_setup):
    """Archived cards no longer appear on the normal board view."""
    visible_card = Card.objects.create(list=board_setup["done_list"], title="Visible")
    archived_card = Card.objects.create(
        list=board_setup["done_list"], title="Archived One"
    )
    archived_card.is_archived = True
    archived_card.archived_at = timezone.now()
    archived_card.save(update_fields=["is_archived", "archived_at"])

    client = Client()
    client.force_login(board_setup["writer"])
    response = client.get(
        reverse(
            "aa_kanban:board_detail", kwargs={"board_slug": board_setup["board"].slug}
        )
    )
    assert response.status_code == 200
    assert visible_card.title.encode() in response.content
    assert archived_card.title.encode() not in response.content


@pytest.mark.django_db
def test_archived_cards_view_lists_archived_cards(board_setup):
    """The archived-cards overview shows archived cards and hides active ones."""
    active_card = Card.objects.create(list=board_setup["done_list"], title="Active")
    archived_card = Card.objects.create(
        list=board_setup["done_list"], title="LongGoneTicket"
    )
    archived_card.is_archived = True
    archived_card.archived_at = timezone.now()
    archived_card.save(update_fields=["is_archived", "archived_at"])

    client = Client()
    client.force_login(board_setup["writer"])
    response = client.get(
        reverse(
            "aa_kanban:archived_cards", kwargs={"board_slug": board_setup["board"].slug}
        )
    )
    assert response.status_code == 200
    assert archived_card.title.encode() in response.content
    assert active_card.title.encode() not in response.content


@pytest.mark.django_db
def test_archived_cards_view_requires_board_access(board_setup, user_factory):
    """Users without view access to the board cannot see its archived cards."""
    outsider = user_factory("archive_outsider")

    client = Client()
    client.force_login(outsider)
    response = client.get(
        reverse(
            "aa_kanban:archived_cards", kwargs={"board_slug": board_setup["board"].slug}
        )
    )
    assert response.status_code == 403
