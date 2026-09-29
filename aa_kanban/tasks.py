import logging

from asgiref.sync import sync_to_async
from celery import shared_task

from .models import Card

logger = logging.getLogger(__name__)


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
            logger.error(f"Discord channel with ID {channel_id} not found by bot.")
            return

        # Prepare mentions
        mentions = []
        try:
            # Attempt to get Discord UID for the creator
            from allianceauth.services.modules.discord.models import DiscordUser

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
            assigned_team_msg = f"**Assigned Team:** {card.assigned_team.name}"
            if card.assigned_team.discord_role_id:
                assigned_team_msg += f" <@&{card.assigned_team.discord_role_id}>"
        thread_name = f"Ticket #{card.id}: {card.title[:80]}"
        message_content = "🎫 **New Ticket Submitted** 🎫\n"
        message_content += f"**Title:** {card.title}\n"
        message_content += (
            f"**Reporter:** {card.created_by.username} {' '.join(mentions)}\n"
        )
        if assigned_team_msg:
            message_content += f"{assigned_team_msg}\n"
        if card.description:
            desc = card.description[:500] + (
                "..." if len(card.description) > 500 else ""
            )
            message_content += f"**Description:**\n```\n{desc}\n```\n"

        import discord

        # Create a thread from a starter message
        try:
            starter_message = await channel.send(content=message_content)
            thread = await starter_message.create_thread(name=thread_name)

            # Save the thread ID on the card
            card.discord_thread_id = thread.id
            await sync_to_async(card.save)(update_fields=["discord_thread_id"])
            logger.info(f"Created Discord thread {thread.id} for card {card.id}")
        except discord.errors.Forbidden:
            logger.error(
                f"Bot lacks permission to create threads in channel {channel_id}"
            )
        except discord.errors.HTTPException as e:
            logger.error(
                f"Discord HTTP Exception creating thread for card {card.id}: {e}"
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
        run_task_function.delay(
            "aa_kanban.tasks._create_discord_thread", task_args=[card_id]
        )
    except ImportError:
        logger.error("aadiscordbot is not installed or available.")
