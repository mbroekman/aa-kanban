"""Search across all boards (TASK-114)."""

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from aa_kanban.models import Board, Card, Comment, KanbanGroup, KanbanTeam, Label
from aa_kanban.search import search_cards, snippet


@pytest.fixture
def make_user(db):
    counter = {"id": 9900}

    def _make(username: str, *perms: str):
        counter["id"] += 1
        user = AuthUtils.create_user(username)
        AuthUtils.add_main_character(
            user, f"Char {username}", character_id=counter["id"]
        )
        AuthUtils.add_permission_to_user_by_name("aa_kanban.basic_access", user)
        for perm in perms:
            AuthUtils.add_permission_to_user_by_name(perm, user)
        return user

    return _make


@pytest.fixture
def world(make_user):
    """Two readable boards, one hidden board and one archived board."""
    owner = make_user("search_owner")
    reader = make_user("search_reader")
    outsider = make_user("search_outsider")
    readers = KanbanGroup.objects.create(name="Search Readers")
    reader.kanban_groups.add(readers)

    open_board = Board.objects.create(name="Ops", slug="ops", created_by=owner)
    open_board.view_groups.add(readers)
    hidden = Board.objects.create(name="Secret", slug="secret", created_by=owner)
    archived = Board.objects.create(
        name="Old",
        slug="old",
        created_by=owner,
        is_archived=True,
        archived_at=timezone.now(),
    )
    archived.view_groups.add(readers)

    todo = open_board.lists.get(name="To Do")
    card = Card.objects.create(
        list=todo,
        title="Refit the Nyx",
        description="Needs **fighters**",
        created_by=owner,
    )
    return {
        "owner": owner,
        "reader": reader,
        "outsider": outsider,
        "open": open_board,
        "hidden": hidden,
        "archived": archived,
        "todo": todo,
        "card": card,
    }


def ids(user, query, **kwargs):
    return {c.pk for c in search_cards(user, query, **kwargs)[0]}


@pytest.mark.django_db
class TestFields:
    def test_title_description_and_card_number(self, world):
        card, reader = world["card"], world["reader"]
        assert ids(reader, "nyx") == {card.pk}
        assert ids(reader, "fighters") == {card.pk}
        assert ids(reader, f"#{card.pk}") == {card.pk}
        assert ids(reader, str(card.pk)) == {card.pk}

    def test_comment_names_label_and_team(self, world, make_user):
        card, reader = world["card"], world["reader"]
        pilot = make_user("Krowez Pilot")
        card.assignees.add(pilot)
        Comment.objects.create(card=card, author=world["owner"], text="Fit with drones")
        card.labels.add(Label.objects.create(name="Logistics", color="info"))
        card.assigned_team = KanbanTeam.objects.create(name="Capital Crew")
        card.save()

        for query in ("drones", "krowez", "search_owner", "logistics", "capital crew"):
            assert ids(reader, query) == {card.pk}, query

    def test_every_word_must_match(self, world):
        Card.objects.create(
            list=world["todo"], title="Refit the Avatar", created_by=world["owner"]
        )
        assert ids(world["reader"], "refit nyx") == {world["card"].pk}

    def test_too_short_query_finds_nothing(self, world):
        assert search_cards(world["reader"], "n") == ([], False)


@pytest.mark.django_db
class TestVisibility:
    def test_hidden_board_is_not_searched(self, world):
        Card.objects.create(
            list=world["hidden"].lists.first(),
            title="Nyx secret",
            created_by=world["owner"],
        )
        assert ids(world["reader"], "nyx") == {world["card"].pk}
        assert ids(world["outsider"], "nyx") == set()

    def test_members_board_is_searched_with_basic_access(self, world):
        world["hidden"].is_members_board = True
        world["hidden"].save()
        card = Card.objects.create(
            list=world["hidden"].lists.first(),
            title="Members nyx",
            created_by=world["owner"],
        )
        assert card.pk in ids(world["outsider"], "nyx")

    def test_archived_board_only_for_managers_and_creator(self, world, make_user):
        card = Card.objects.create(
            list=world["archived"].lists.first(),
            title="Old nyx",
            created_by=world["owner"],
        )
        manager = make_user("search_manager", "aa_kanban.manage_boards")
        assert card.pk not in ids(world["reader"], "nyx")
        assert card.pk in ids(world["owner"], "nyx")
        assert card.pk in ids(manager, "nyx")

    def test_own_cards_only_board(self, world, make_user):
        board = world["open"]
        board.own_cards_only = True
        board.save()
        reader = world["reader"]
        mine = Card.objects.create(
            list=world["todo"], title="Nyx for reader", created_by=reader
        )
        team = KanbanTeam.objects.create(name="Reader team")
        team.members.add(reader)
        via_team = Card.objects.create(
            list=world["todo"],
            title="Nyx team",
            created_by=world["owner"],
            assigned_team=team,
        )

        assert ids(reader, "nyx") == {mine.pk, via_team.pk}
        assert world["card"].pk in ids(world["owner"], "nyx")

    def test_archived_cards_only_when_asked(self, world):
        card = world["card"]
        card.is_archived = True
        card.archived_at = timezone.now()
        card.save()
        assert ids(world["reader"], "nyx") == set()
        assert ids(world["reader"], "nyx", include_archived=True) == {card.pk}


@pytest.mark.django_db
def test_limit_keeps_title_matches_first(world):
    for i in range(3):
        Card.objects.create(
            list=world["todo"],
            title=f"Other {i}",
            description="nyx",
            created_by=world["owner"],
        )
    cards, truncated = search_cards(world["reader"], "nyx", limit=2)
    assert truncated
    assert cards[0].pk == world["card"].pk


def test_snippet_centres_on_the_match():
    text = "a " * 100 + "the Nyx needs fighters " + "b " * 100
    result = snippet(text, ["nyx"])
    assert "Nyx" in result and result.startswith("…") and result.endswith("…")
    assert snippet("nothing here", ["nyx"]) == ""


@pytest.mark.django_db
class TestPage:
    def test_results_link_to_the_card(self, world):
        client = Client()
        client.force_login(world["reader"])
        response = client.get(reverse("aa_kanban:search"), {"q": "nyx"})
        assert response.status_code == 200
        html = response.content.decode()
        assert f"/board/ops/?card={world['card'].pk}" in html
        assert "<mark>Nyx</mark>" in html

    def test_archived_result_links_to_archive_page(self, world):
        card = world["card"]
        card.is_archived = True
        card.archived_at = timezone.now()
        card.save()
        client = Client()
        client.force_login(world["reader"])
        html = client.get(
            reverse("aa_kanban:search"), {"q": "nyx", "archived": "1"}
        ).content.decode()
        assert f"/board/ops/archived/?card={card.pk}" in html

    def test_search_box_on_overview_and_board(self, world):
        client = Client()
        client.force_login(world["reader"])
        search_url = reverse("aa_kanban:search")
        for url in (
            reverse("aa_kanban:index"),
            reverse("aa_kanban:board_detail", args=["ops"]),
        ):
            assert search_url in client.get(url).content.decode(), url

    def test_highlight_escapes_html(self, world):
        Card.objects.create(
            list=world["todo"], title="<b>nyx</b>", created_by=world["owner"]
        )
        client = Client()
        client.force_login(world["reader"])
        html = client.get(reverse("aa_kanban:search"), {"q": "nyx"}).content.decode()
        assert "&lt;b&gt;<mark>nyx</mark>&lt;/b&gt;" in html

    def test_needs_basic_access(self, db):
        user = AuthUtils.create_user("no_access_searcher")
        AuthUtils.add_main_character(user, "No Access", character_id=9999)
        client = Client()
        client.force_login(user)
        assert client.get(reverse("aa_kanban:search"), {"q": "nyx"}).status_code == 403
