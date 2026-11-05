"""Card counts and attention signals on the board overview (TASK-108)."""

from datetime import timedelta

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from aa_kanban.board_stats import board_stats
from aa_kanban.models import Board, Card, Comment, List


def make_board(name="Ops", stale_hours=0):
    board = Board.objects.create(name=name, stale_card_alert_hours=stale_hours)
    board.lists.all().delete()  # drop the default columns; "Shipped" is last
    todo = List.objects.create(board=board, name="To Do", order=0)
    doing = List.objects.create(board=board, name="Doing", order=1)
    finished = List.objects.create(board=board, name="Shipped", order=2)
    return board, todo, doing, finished


def age(card, hours):
    Card.objects.filter(pk=card.pk).update(
        updated_at=timezone.now() - timedelta(hours=hours)
    )


@pytest.mark.django_db
class TestBoardStats:
    def test_counts_cards_but_not_archived_ones(self):
        board, todo, doing, finished = make_board()
        Card.objects.create(list=todo, title="a")
        Card.objects.create(list=doing, title="b")
        Card.objects.create(list=finished, title="c")
        Card.objects.create(list=finished, title="old", is_archived=True)

        stats = board_stats([board])[board.id]

        assert stats.card_count == 3
        assert not stats.needs_attention

    def test_overdue_card_needs_attention(self):
        board, todo, _, finished = make_board()
        past = timezone.now() - timedelta(days=1)
        Card.objects.create(list=todo, title="late", due_date=past)
        Card.objects.create(
            list=todo, title="later", due_date=timezone.now() + timedelta(days=1)
        )
        Card.objects.create(list=finished, title="done late", due_date=past)

        stats = board_stats([board])[board.id]

        assert stats.overdue == 1
        assert stats.needs_attention

    def test_inactive_card_uses_board_stale_hours_and_comments(self):
        board, todo, doing, finished = make_board(stale_hours=48)
        quiet = Card.objects.create(list=todo, title="quiet")
        age(quiet, 72)
        talked = Card.objects.create(list=doing, title="talked about")
        Comment.objects.create(card=talked, text="still on it")
        age(talked, 72)
        recent = Card.objects.create(list=doing, title="recent")
        age(recent, 10)
        done = Card.objects.create(list=finished, title="done")
        age(done, 500)

        stats = board_stats([board])[board.id]

        assert stats.inactive == 1

    def test_no_inactive_signal_when_stale_alerts_are_off(self):
        board, todo, _, _ = make_board(stale_hours=0)
        card = Card.objects.create(list=todo, title="quiet")
        age(card, 1000)

        assert board_stats([board])[board.id].inactive == 0

    def test_done_named_list_counts_as_finished(self):
        board, todo, _, _ = make_board()
        List.objects.create(board=board, name="Afgerond", order=1)
        done_named = board.lists.get(name="Afgerond")
        Card.objects.create(
            list=done_named, title="x", due_date=timezone.now() - timedelta(days=1)
        )

        assert board_stats([board])[board.id].overdue == 0

    def test_column_over_wip_limit(self):
        board, _, doing, _ = make_board()
        doing.wip_limit = 1
        doing.save()
        Card.objects.create(list=doing, title="a")
        Card.objects.create(list=doing, title="b")

        stats = board_stats([board])[board.id]

        assert stats.over_wip == ["Doing"]
        assert stats.needs_attention

    def test_query_count_does_not_grow_with_boards(self, django_assert_num_queries):
        boards = [make_board(name=f"B{i}")[0] for i in range(4)]
        for board in boards:
            Card.objects.create(list=board.lists.first(), title="x")

        with django_assert_num_queries(2):
            board_stats(boards)


@pytest.mark.django_db
def test_dashboard_shows_card_count_and_attention():
    user = AuthUtils.create_user("viewer")
    AuthUtils.add_main_character(user, "Viewer", character_id=4242)
    AuthUtils.add_permission_to_user_by_name("aa_kanban.basic_access", user)
    board, todo, _, _ = make_board(name="Recruitment")
    board.created_by = user
    board.save()
    Card.objects.create(
        list=todo, title="late", due_date=timezone.now() - timedelta(days=2)
    )
    Card.objects.create(list=todo, title="fine")
    client = Client()
    client.force_login(user)

    response = client.get(reverse("aa_kanban:index"))

    assert response.status_code == 200
    html = response.content.decode()
    assert "Cards need attention" in html
    assert "1 card past its due date" in html
    assert '<span class="fw-bold">2</span> cards' in html


@pytest.mark.django_db
def test_attention_reasons_are_translated():
    from django.template.loader import render_to_string
    from django.test import RequestFactory
    from django.utils import translation

    user = AuthUtils.create_user("nl_viewer")
    board, todo, _, _ = make_board(name="Logistiek")
    Card.objects.create(
        list=todo, title="late", due_date=timezone.now() - timedelta(days=2)
    )
    board.stats = board_stats([board])[board.id]
    request = RequestFactory().get("/")
    request.user = user

    with translation.override("nl"):
        html = render_to_string(
            "aa_kanban/index.html", {"boards": [board]}, request=request
        )

    assert "1 kaart over de deadline" in html
    assert "kaarten" in html
