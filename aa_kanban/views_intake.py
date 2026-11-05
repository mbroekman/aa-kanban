"""Intake API for the Discord thread router: a new Discord thread becomes a card.

The router (github.com/mbroekman/discord-thread-router) holds the channel rules and sends
the board, list, labels and team with every thread. Authenticated with an
IntakeApiKey (Bearer), not with a session.
"""

import json
import logging

from django.apps import apps
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Board, Card, IntakeApiKey, KanbanTeam, Label
from .services import create_kanban_card

logger = logging.getLogger(__name__)

SERVICE_USERNAME = "discord-intake"


def service_user() -> User:
    """The user that 'creates' cards for Discord users without an Auth account."""
    user, created = User.objects.get_or_create(
        username=SERVICE_USERNAME,
        defaults={"first_name": "Discord intake", "is_active": False},
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    return user


def auth_user_for_discord_id(discord_id) -> User | None:
    """The Auth user linked to this Discord account (Alliance Auth's own Discord service)."""
    if not discord_id or not apps.is_installed("allianceauth.services.modules.discord"):
        return None
    from allianceauth.services.modules.discord.models import DiscordUser

    link = DiscordUser.objects.filter(uid=discord_id).select_related("user").first()
    return link.user if link else None


def _description(data: dict, linked: bool) -> str:
    content = str(data.get("content") or "").strip()
    author = str(data.get("author_name") or "unknown")
    source = f"*Opened in Discord by {author}*"
    if not linked:
        source += " *(no Auth account linked)*"
    jump_url = str(data.get("jump_url") or "")
    if jump_url.startswith("https://"):
        source += f" — [Discord thread]({jump_url})"
    return f"{content}\n\n---\n{source}" if content else source


def _card_reply(
    request: HttpRequest, card: Card, status: int, skipped=()
) -> JsonResponse:
    board = card.list.board
    url = request.build_absolute_uri(
        reverse("aa_kanban:board_detail", args=[board.slug])
    )
    return JsonResponse(
        {
            "card_id": card.id,
            "card_url": f"{url}?card={card.id}",
            "board_name": board.name,
            "skipped": list(skipped),
        },
        status=status,
    )


@csrf_exempt
@require_POST
def discord_thread_intake(request: HttpRequest) -> JsonResponse:
    header = request.headers.get("Authorization", "")
    key = IntakeApiKey.lookup(header[7:] if header.startswith("Bearer ") else "")
    if not key:
        return JsonResponse({"error": "Invalid or missing API key."}, status=401)
    IntakeApiKey.objects.filter(pk=key.pk).update(last_used_at=timezone.now())

    try:
        data = json.loads(request.body)
        thread_id = int(data["thread_id"])
        title = str(data["title"]).strip()[:255]
        board_slug = str(data["board"])
    except (ValueError, KeyError, TypeError):
        return JsonResponse(
            {"error": "Send JSON with at least board, thread_id and title."}, status=400
        )
    if not title:
        return JsonResponse({"error": "The title is empty."}, status=400)

    with transaction.atomic():
        # Lock the board so two events for one thread cannot both create a card.
        board = Board.objects.select_for_update().filter(slug=board_slug).first()
        if not board:
            return JsonResponse({"error": "Unknown board."}, status=404)
        if board.is_archived:
            return JsonResponse({"error": "The board is archived."}, status=409)
        existing = Card.objects.filter(discord_thread_id=thread_id).first()
        if existing:
            return _card_reply(request, existing, 200)
        if not board.lists.exists():
            return JsonResponse({"error": "The board has no lists."}, status=409)

        skipped = []
        label_names = [str(n) for n in data.get("labels") or []]
        labels = dict(
            Label.objects.filter(name__in=label_names).values_list("name", "id")
        )
        skipped += [f"label {n}" for n in label_names if n not in labels]
        team = None
        if data.get("team"):
            team = KanbanTeam.objects.filter(name__iexact=str(data["team"])).first()
            if not team:
                skipped.append(f"team {data['team']}")
        list_name = str(data.get("list") or "")
        if list_name and not board.lists.filter(name__iexact=list_name).exists():
            skipped.append(f"list {list_name}")

        linked_user = auth_user_for_discord_id(data.get("author_discord_id"))
        card = create_kanban_card(
            board_id=board.id,
            title=title,
            creator=linked_user or service_user(),
            description=_description(data, linked=bool(linked_user)),
            column_name=list_name,
            label_ids=list(labels.values()),
        )
        card.discord_thread_id = thread_id
        card.assigned_team = team
        card.save(update_fields=["discord_thread_id", "assigned_team", "updated_at"])

    logger.info(
        "Discord thread %s became card %s on board %s", thread_id, card.id, board.slug
    )
    return _card_reply(request, card, 201, skipped)
