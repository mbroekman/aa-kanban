import logging

from asgiref.sync import sync_to_async
from celery import shared_task
from django.utils.translation import gettext as _

from .models import Board, Card

try:
    from allianceauth.services.modules.discord.models import DiscordUser
except ImportError:
    DiscordUser = None

logger = logging.getLogger(__name__)


async def _send_stale_cards_discord(bot, channel_id: int, message_content: str):
    """Async task run inside aadiscordbot to send stale card alerts to a Discord channel."""
    try:
        channel = bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await bot.fetch_channel(channel_id)
            except Exception as e:
                logger.error(
                    f"Discord channel with ID {channel_id} not found by bot: {e}"
                )
                return

        # Discord message limit is 2000 chars
        if len(message_content) <= 1900:
            await channel.send(content=message_content)
        else:
            chunks = []
            for i in range(0, len(message_content), 1800):
                end_idx = i + 1800
                chunks.append(message_content[i:end_idx])
            for chunk in chunks:
                await channel.send(content=chunk)

        logger.info(f"Sent stale cards notification to Discord channel {channel_id}")
    except Exception as e:
        logger.exception(f"Error in _send_stale_cards_discord: {e}")


def format_stale_cards_message(board, stale_cards) -> str:
    """Format a Discord message summarizing stale cards on a board."""
    from django.conf import settings
    from django.urls import reverse
    from django.utils import timezone

    count = len(stale_cards)
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    try:
        board_path = reverse(
            "aa_kanban:board_detail", kwargs={"board_slug": board.slug}
        )
    except Exception:
        board_path = f"/kanban/board/{board.slug}/"
    board_url = f"{site_url}{board_path}" if site_url else board_path

    now = timezone.now()
    header = _(
        "⚠️ **Kanban Alert: Stale Cards on '{board_name}'** ⚠️\n"
        "There are **{count}** card(s) that have been inactive for more than **{hours}** hour(s):\n"
    ).format(
        board_name=board.name,
        count=count,
        hours=board.stale_card_alert_hours,
    )

    lines = [str(header)]
    max_display = 15
    for card in stale_cards[:max_display]:
        last_activity = card.updated_at
        if (
            hasattr(card, "last_comment_time")
            and card.last_comment_time
            and card.last_comment_time > last_activity
        ):
            last_activity = card.last_comment_time

        diff = now - last_activity
        hours_inactive = int(diff.total_seconds() // 3600)
        days = hours_inactive // 24
        remaining_hours = hours_inactive % 24
        if days > 0:
            duration_str = f"{days}d {remaining_hours}h"
        else:
            duration_str = f"{hours_inactive}h"

        assignee_names = [u.username for u in card.assignees.all()]
        assignee_str = (
            ", ".join(assignee_names) if assignee_names else str(_("Unassigned"))
        )

        lines.append(
            str(
                _(
                    "• **{title}** (List: `{list_name}`, Inactive: **{duration}**, Assigned: {assignees})"
                ).format(
                    title=card.title,
                    list_name=card.list.name,
                    duration=duration_str,
                    assignees=assignee_str,
                )
            )
        )

    if count > max_display:
        lines.append(
            str(
                _("\n*... and {extra_count} more card(s).*").format(
                    extra_count=count - max_display
                )
            )
        )

    lines.append(str(_("\n🔗 [View Board]({url})").format(url=board_url)))
    return "\n".join(lines)


@shared_task
def check_stale_cards():
    """Periodically check all boards with stale_card_alert_hours configured and alert Discord."""
    from aa_kanban.utils import send_discord_webhook

    boards = Board.objects.filter(stale_card_alert_hours__gt=0)
    for board in boards:
        stale_cards = list(board.get_stale_cards())
        if not stale_cards:
            continue

        message = format_stale_cards_message(board, stale_cards)
        channel_id = board.discord_alert_channel_id or board.discord_ticket_channel_id
        webhook_url = board.discord_alert_webhook or board.discord_webhook_cards

        sent_bot = False
        alert_dispatched = False
        if channel_id:
            try:
                from aadiscordbot.tasks import run_task_function

                run_task_function.apply_async(
                    args=["aa_kanban.tasks._send_stale_cards_discord"],
                    kwargs={
                        "task_args": [channel_id, message],
                        "task_kwargs": {},
                    },
                    queue="aadiscordbot",
                )
                sent_bot = True
                alert_dispatched = True
            except ImportError:
                logger.warning(
                    "aadiscordbot is not available, falling back to webhook if configured."
                )

        if not sent_bot and webhook_url:
            send_discord_webhook(webhook_url, message)
            alert_dispatched = True

        if alert_dispatched:
            from django.utils import timezone

            Card.objects.filter(pk__in=[c.pk for c in stale_cards]).update(
                last_stale_alert_at=timezone.now()
            )


async def _create_discord_thread(bot, card_id: int):
    try:
        # Load card and settings asynchronously
        card = await sync_to_async(
            Card.objects.select_related(
                "assigned_team", "created_by", "list__board"
            ).get
        )(pk=card_id)

        # Prioritize the board's specific ticket channel
        channel_id = card.list.board.discord_ticket_channel_id
        if not channel_id:
            logger.warning(
                "No ticket_channel_id configured on board, skipping Discord thread creation."
            )
            return

        channel = bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await bot.fetch_channel(channel_id)
            except Exception as e:
                logger.error(
                    f"Discord channel with ID {channel_id} not found by bot: {e}"
                )
                return

        # Prepare mentions
        mentions = []
        if DiscordUser:
            try:
                creator_discord = await sync_to_async(
                    DiscordUser.objects.filter(user=card.created_by).first
                )()
                if creator_discord:
                    mentions.append(f"<@{creator_discord.uid}>")
            except Exception as e:
                logger.warning(
                    f"Could not fetch discord user for {card.created_by.username}: {e}"
                )

        assigned_team_msg = ""
        if card.assigned_team:
            assigned_team_msg = _("**Assigned Team:** {team_name}").format(
                team_name=card.assigned_team.name
            )
            if card.assigned_team.discord_role_id:
                assigned_team_msg += f" <@&{card.assigned_team.discord_role_id}>"
        thread_name = _("Ticket #{card_id}: {card_title}").format(
            card_id=card.id, card_title=card.title[:80]
        )
        message_content = _("🎫 **New Ticket Submitted** 🎫\n")
        message_content += _("**Title:** {card_title}\n").format(card_title=card.title)
        message_content += _("**Reporter:** {username} {mentions}\n").format(
            username=card.created_by.username, mentions=" ".join(mentions)
        )
        if assigned_team_msg:
            message_content += f"{assigned_team_msg}\n"
        if card.description:
            desc = card.description[:500] + (
                "..." if len(card.description) > 500 else ""
            )
            message_content += f"**Description:**\n```\n{desc}\n```\n"

        try:
            import discord
        except ImportError:
            discord = None

        # Create a thread from a starter message
        try:
            starter_message = await channel.send(content=message_content)
            thread = await starter_message.create_thread(name=thread_name)

            # Save the thread ID on the card
            card.discord_thread_id = thread.id
            await sync_to_async(card.save)(update_fields=["discord_thread_id"])
            logger.info(f"Created Discord thread {thread.id} for card {card.id}")

            # Auto-invite team members if a team is assigned
            if card.assigned_team and DiscordUser:
                try:
                    all_team_members = await sync_to_async(list)(
                        card.assigned_team.get_all_members()
                    )
                    team_discord_users = await sync_to_async(list)(
                        DiscordUser.objects.filter(user__in=all_team_members)
                    )
                    for du in team_discord_users:
                        try:
                            user_target = (
                                discord.Object(id=du.uid)
                                if discord and hasattr(discord, "Object")
                                else type("DiscordObject", (), {"id": du.uid})()
                            )
                            await thread.add_user(user_target)
                        except Exception as add_err:
                            logger.warning(
                                f"Failed to auto-invite DiscordUser {du.uid} to thread: {add_err}"
                            )
                except Exception as team_err:
                    logger.warning(
                        f"Error fetching Discord users for auto-invite: {team_err}"
                    )

        except Exception as e:
            if (
                discord
                and hasattr(discord, "errors")
                and isinstance(
                    e, (discord.errors.Forbidden, discord.errors.HTTPException)
                )
            ):
                logger.error(f"Discord error creating thread for card {card.id}: {e}")
            else:
                logger.exception(
                    f"Error creating Discord thread for card {card.id}: {e}"
                )

    except Card.DoesNotExist:
        logger.error(f"Card {card_id} does not exist.")
    except Exception as e:
        logger.exception(f"Error in _create_discord_thread: {e}")


@shared_task
def create_ticket_thread(card_id: int):
    """
    Celery task that delegates to aadiscordbot's run_task_function
    to run async code in the discord bot context.
    """
    try:
        from aadiscordbot.tasks import run_task_function

        # Instruct aadiscordbot to run our async function inside its event loop
        run_task_function.apply_async(
            args=["aa_kanban.tasks._create_discord_thread"],
            kwargs={"task_args": [card_id], "task_kwargs": {}},
            queue="aadiscordbot",
        )
    except ImportError:
        logger.error("aadiscordbot is not installed or available.")


async def _send_discord_thread_message(
    bot,
    thread_id: int,
    message_content: str,
    team_id: int | None = None,
):
    """Send an update message to a Discord ticket thread, optionally auto-inviting new team members."""
    try:
        thread = bot.get_channel(thread_id)
        if not thread:
            try:
                thread = await bot.fetch_channel(thread_id)
            except Exception as e:
                logger.error(
                    f"Discord thread with ID {thread_id} not found by bot: {e}"
                )
                return

        await thread.send(content=message_content)
        logger.info(f"Posted update message to Discord thread {thread_id}")

        if team_id:
            from .models import KanbanTeam

            try:
                team = await sync_to_async(KanbanTeam.objects.get)(pk=team_id)
                try:
                    import discord
                except ImportError:
                    discord = None

                if DiscordUser:
                    all_team_members = await sync_to_async(list)(team.get_all_members())
                    team_discord_users = await sync_to_async(list)(
                        DiscordUser.objects.filter(user__in=all_team_members)
                    )
                for du in team_discord_users:
                    try:
                        user_target = (
                            discord.Object(id=du.uid)
                            if discord and hasattr(discord, "Object")
                            else type("DiscordObject", (), {"id": du.uid})()
                        )
                        await thread.add_user(user_target)
                    except Exception as add_err:
                        logger.warning(
                            f"Failed to auto-invite user {du.uid} to thread: {add_err}"
                        )
            except Exception as team_err:
                logger.warning(
                    f"Error auto-inviting team members to thread: {team_err}"
                )

    except Exception as e:
        logger.exception(f"Error in _send_discord_thread_message: {e}")


@shared_task
def notify_ticket_thread(
    thread_id: int, message_content: str, team_id: int | None = None
):
    """Celery task to post an update message to a card's Discord thread."""
    if not thread_id:
        return

    try:
        from aadiscordbot.tasks import run_task_function

        run_task_function.apply_async(
            args=["aa_kanban.tasks._send_discord_thread_message"],
            kwargs={
                "task_args": [thread_id, str(message_content)],
                "task_kwargs": {"team_id": team_id},
            },
            queue="aadiscordbot",
        )
    except ImportError:
        logger.warning("aadiscordbot is not installed or available.")
