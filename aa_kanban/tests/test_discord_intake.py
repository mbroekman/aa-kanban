"""Discord thread intake API for the thread router (TASK-107)."""

import json
from unittest.mock import patch

import pytest
from allianceauth.services.modules.discord.models import DiscordUser
from allianceauth.tests.auth_utils import AuthUtils
from django.test import Client
from django.urls import reverse

from aa_kanban.models import Board, Card, IntakeApiKey, KanbanTeam, Label
from aa_kanban.views_intake import SERVICE_USERNAME

URL = reverse("aa_kanban:intake_discord_thread")


@pytest.fixture
def api_key(db):
    key = IntakeApiKey(name="router")
    raw = key.set_new_key()
    key.save()
    return raw


@pytest.fixture
def board(db):
    # A new board gets the default lists: Backlog, To Do, In Progress, ...
    return Board.objects.create(name="Corp Tickets", slug="corp-tickets")


def post(data, key):
    headers = {"HTTP_AUTHORIZATION": f"Bearer {key}"} if key else {}
    return Client().post(
        URL, json.dumps(data), content_type="application/json", **headers
    )


def thread(**extra):
    data = {
        "board": "corp-tickets",
        "thread_id": 1111,
        "title": "Jump bridge offline",
        "content": "The JB in 9O- is down.",
        "author_discord_id": 777,
        "author_name": "Pilot",
        "jump_url": "https://discord.com/channels/1/1111",
    }
    data.update(extra)
    return data


@pytest.mark.django_db
def test_thread_becomes_card_on_board_list_with_labels_and_team(api_key, board):
    Label.objects.create(name="Discord")
    team = KanbanTeam.objects.create(name="IT")

    response = post(
        thread(list="in progress", labels=["Discord", "Nope"], team="it"), api_key
    )

    assert response.status_code == 201
    body = response.json()
    card = Card.objects.get(pk=body["card_id"])
    assert card.list.name == "In Progress"
    assert card.title == "Jump bridge offline"
    assert card.discord_thread_id == 1111
    assert card.assigned_team == team
    assert list(card.labels.values_list("name", flat=True)) == ["Discord"]
    assert "The JB in 9O- is down." in card.description
    assert "https://discord.com/channels/1/1111" in card.description
    assert body["skipped"] == ["label Nope"]
    assert body["card_url"].endswith(f"/board/corp-tickets/?card={card.id}")
    assert body["board_name"] == "Corp Tickets"
    assert IntakeApiKey.objects.get().last_used_at is not None


@pytest.mark.django_db
def test_second_event_for_same_thread_returns_existing_card(api_key, board):
    first = post(thread(), api_key)
    second = post(thread(title="other"), api_key)
    assert second.status_code == 200
    assert second.json()["card_id"] == first.json()["card_id"]
    assert Card.objects.count() == 1


@pytest.mark.django_db
def test_linked_discord_user_is_creator_else_service_user(api_key, board):
    user = AuthUtils.create_user("linked")
    DiscordUser.objects.create(user=user, uid=777)
    card = Card.objects.get(pk=post(thread(), api_key).json()["card_id"])
    assert card.created_by == user
    assert "no Auth account" not in card.description

    card = Card.objects.get(
        pk=post(thread(thread_id=2222, author_discord_id=888), api_key).json()[
            "card_id"
        ]
    )
    assert card.created_by.username == SERVICE_USERNAME
    assert not card.created_by.is_active
    assert "no Auth account linked" in card.description


@pytest.mark.django_db
def test_unknown_list_falls_back_to_first_list(api_key, board):
    body = post(thread(list="Doing"), api_key).json()
    assert Card.objects.get(pk=body["card_id"]).list.name == "Backlog"
    assert body["skipped"] == ["list Doing"]


@pytest.mark.django_db
@pytest.mark.parametrize("key", [None, "wrong"])
def test_missing_or_wrong_key_is_refused(api_key, board, key):
    assert post(thread(), key).status_code == 401
    assert not Card.objects.exists()


@pytest.mark.django_db
def test_inactive_key_is_refused(api_key, board):
    IntakeApiKey.objects.update(is_active=False)
    assert post(thread(), api_key).status_code == 401


@pytest.mark.django_db
def test_unknown_board_and_bad_payload(api_key, board):
    assert post(thread(board="nope"), api_key).status_code == 404
    assert post({"board": "corp-tickets"}, api_key).status_code == 400
    assert post(thread(title="   "), api_key).status_code == 400
    assert Client().get(URL).status_code == 405


@pytest.mark.django_db
def test_board_webhook_still_fires(api_key, board):
    board.discord_webhook_cards = "https://discord.example/webhook"
    board.save()
    with patch("aa_kanban.utils.send_discord_webhook") as webhook:
        post(thread(), api_key)
    webhook.assert_called_once()


@pytest.mark.django_db
def test_only_the_hash_is_stored():
    key = IntakeApiKey(name="x")
    raw = key.set_new_key()
    key.save()
    assert raw not in (key.key_hash, key.prefix * 5)
    assert key.prefix == raw[:8]
    assert IntakeApiKey.lookup(raw) == key
    assert IntakeApiKey.lookup("") is None


@pytest.mark.django_db
def test_other_kanban_pages_still_need_a_login():
    # Alliance Auth stops decorating after an excluded view; the intake URL is last.
    from aa_kanban import urls

    assert urls.urlpatterns[-1].name == "intake_discord_thread"
    for name in ("index", "summary"):
        response = Client().get(reverse(f"aa_kanban:{name}"))
        assert response.status_code == 302 and "/login/" in response.url
    response = Client().post(
        reverse("aa_kanban:remove_authgroup_from_team", args=[1, 1])
    )
    assert response.status_code == 302 and "/login/" in response.url
