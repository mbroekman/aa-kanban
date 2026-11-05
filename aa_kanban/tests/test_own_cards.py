"""Boards that show readers only their own cards (TASK-111)."""

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.test import Client
from django.urls import reverse

from aa_kanban.board_stats import board_stats
from aa_kanban.models import Board, Card, KanbanGroup, KanbanTeam


def member(username, *perms):
    user = AuthUtils.create_user(username)
    AuthUtils.add_main_character(
        user, username, character_id=abs(hash(username)) % 10**8
    )
    AuthUtils.add_permission_to_user_by_name("aa_kanban.basic_access", user)
    for perm in perms:
        AuthUtils.add_permission_to_user_by_name(perm, user)
    return user


def client_for(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def setup(db):
    manager = member("manager", "aa_kanban.manage_boards")
    writer = member("writer")
    alice = member("alice")
    bob = member("bob")
    writers = KanbanGroup.objects.create(name="Writers")
    writers.members.add(writer)
    board = Board.objects.create(
        name="Requests", is_members_board=True, own_cards_only=True
    )
    board.lists.all().delete()
    board.write_groups.add(writers)
    first = board.lists.create(name="New", order=0)
    second = board.lists.create(name="Doing", order=1)
    alice_card = Card.objects.create(list=first, title="Alice asks", created_by=alice)
    bob_card = Card.objects.create(list=first, title="Bob asks", created_by=bob)
    assigned = Card.objects.create(list=second, title="For Alice", created_by=writer)
    assigned.assignees.add(alice)
    return {
        "manager": manager,
        "writer": writer,
        "alice": alice,
        "bob": bob,
        "board": board,
        "first": first,
        "second": second,
        "alice_card": alice_card,
        "bob_card": bob_card,
        "assigned": assigned,
    }


def board_titles(response):
    return sorted(c.title for lst in response.context["lists"] for c in lst.cards.all())


@pytest.mark.django_db
class TestVisibility:
    def test_reader_sees_created_and_assigned_cards_only(self, setup):
        url = reverse("aa_kanban:board_detail", args=[setup["board"].slug])
        response = client_for(setup["alice"]).get(url)

        assert board_titles(response) == ["Alice asks", "For Alice"]
        assert "Bob asks" not in response.content.decode()

    def test_team_assignment_counts_as_own(self, setup):
        team = KanbanTeam.objects.create(name="Haulers")
        team.members.add(setup["bob"])
        setup["assigned"].assigned_team = team
        setup["assigned"].save()

        assert setup["assigned"].can_user_view(setup["bob"])

    def test_writers_and_managers_see_everything(self, setup):
        url = reverse("aa_kanban:board_detail", args=[setup["board"].slug])
        for who in ("writer", "manager"):
            response = client_for(setup[who]).get(url)
            assert board_titles(response) == ["Alice asks", "Bob asks", "For Alice"]

    def test_setting_off_shows_everything(self, setup):
        setup["board"].own_cards_only = False
        setup["board"].save()
        url = reverse("aa_kanban:board_detail", args=[setup["board"].slug])

        response = client_for(setup["alice"]).get(url)

        assert len(board_titles(response)) == 3

    def test_opening_someone_elses_card_is_forbidden(self, setup):
        alice = client_for(setup["alice"])
        own = alice.get(reverse("aa_kanban:card_modal", args=[setup["alice_card"].pk]))
        other = alice.get(reverse("aa_kanban:card_modal", args=[setup["bob_card"].pk]))

        assert own.status_code == 200
        assert other.status_code == 403

    def test_archived_cards_are_filtered(self, setup):
        Card.objects.filter(
            pk__in=[setup["alice_card"].pk, setup["bob_card"].pk]
        ).update(is_archived=True)
        url = reverse("aa_kanban:archived_cards", args=[setup["board"].slug])

        response = client_for(setup["alice"]).get(url)

        assert [c.title for c in response.context["cards"]] == ["Alice asks"]

    def test_dashboard_counts_own_cards(self, setup):
        stats = board_stats([setup["board"]], setup["alice"])
        assert stats[setup["board"].id].card_count == 2
        stats = board_stats([setup["board"]], setup["writer"])
        assert stats[setup["board"].id].card_count == 3

    def test_summary_filters_own_cards_boards(self, setup):
        # The summary lists management boards; give alice read access to one.
        readers = KanbanGroup.objects.create(name="Readers")
        readers.members.add(setup["alice"])
        board = setup["board"]
        board.is_members_board = False
        board.save()
        board.view_groups.add(readers)

        response = client_for(setup["alice"]).get(reverse("aa_kanban:summary"))

        titles = sorted(
            c.title
            for b in response.context["boards"]
            for lst in b.lists.all()
            for c in lst.cards.all()
        )
        assert titles == ["Alice asks", "For Alice"]


@pytest.mark.django_db
class TestEditing:
    def test_reader_adds_card_in_first_column_only(self, setup):
        alice = client_for(setup["alice"])

        first = alice.post(
            reverse("aa_kanban:create_card", args=[setup["first"].pk]),
            {"title": "Mine"},
        )
        second = alice.post(
            reverse("aa_kanban:create_card", args=[setup["second"].pk]), {"title": "No"}
        )

        assert first.status_code == 200
        assert Card.objects.filter(title="Mine", created_by=setup["alice"]).exists()
        assert second.status_code == 403

    def test_board_page_shows_add_form_only_on_first_column(self, setup):
        url = reverse("aa_kanban:board_detail", args=[setup["board"].slug])
        html = client_for(setup["alice"]).get(url).content.decode()

        assert reverse("aa_kanban:create_card", args=[setup["first"].pk]) in html
        assert reverse("aa_kanban:create_card", args=[setup["second"].pk]) not in html

    def test_reader_edits_and_comments_on_own_card(self, setup):
        alice = client_for(setup["alice"])
        card = setup["alice_card"]

        alice.post(reverse("aa_kanban:update_card", args=[card.pk]), {"title": "Fixed"})
        comment = alice.post(
            reverse("aa_kanban:add_comment", args=[card.pk]), {"comment": "Any news?"}
        )

        card.refresh_from_db()
        assert card.title == "Fixed"
        assert comment.status_code == 200
        assert card.comments.count() == 1

    def test_reader_cannot_edit_someone_elses_card(self, setup):
        alice = client_for(setup["alice"])
        card = setup["bob_card"]

        update = alice.post(
            reverse("aa_kanban:update_card", args=[card.pk]), {"title": "Hacked"}
        )
        comment = alice.post(
            reverse("aa_kanban:add_comment", args=[card.pk]), {"comment": "Hi"}
        )

        assert update.status_code == 403
        assert comment.status_code == 403

    def test_board_actions_stay_with_writers(self, setup):
        alice = client_for(setup["alice"])
        card = setup["alice_card"]

        move = alice.post(
            reverse("aa_kanban:move_card", args=[card.pk]),
            {"target_list_id": setup["second"].pk, "new_position": 0},
        )
        delete = alice.post(reverse("aa_kanban:delete_card", args=[card.pk]))
        color = alice.post(
            reverse("aa_kanban:update_card_color", args=[card.pk]), {"color": "danger"}
        )

        assert {move.status_code, delete.status_code, color.status_code} == {403}

    def test_plain_members_board_stays_read_only(self, setup):
        board = setup["board"]
        board.own_cards_only = False
        board.save()

        response = client_for(setup["alice"]).post(
            reverse("aa_kanban:create_card", args=[setup["first"].pk]), {"title": "No"}
        )

        assert response.status_code == 403

    def test_edit_board_form_sets_the_flag(self, setup):
        board = Board.objects.create(name="Ops", created_by=setup["manager"])
        client_for(setup["manager"]).post(
            reverse("aa_kanban:edit_board", args=[board.slug]),
            {"name": "Ops", "own_cards_only": "on"},
        )
        board.refresh_from_db()
        assert board.own_cards_only
