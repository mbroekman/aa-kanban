import logging
import discord
from discord.ext import commands
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class KanbanTicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def sync_ticket_comment(self, message: discord.Message):
        # Ignore bot messages
        if message.author.bot:
            return

        # Check if the channel is a thread
        if not isinstance(message.channel, discord.Thread):
            return

        # Check if this thread belongs to a Card
        from .models import Card, Comment
        try:
            card = await sync_to_async(Card.objects.get)(discord_thread_id=message.channel.id)
            
            # Find the user who sent it
            from allianceauth.services.modules.discord.models import DiscordUser
            discord_user = await sync_to_async(
                DiscordUser.objects.filter(uid=message.author.id).select_related('user').first
            )()
            user = discord_user.user if discord_user else None

            content = message.content
            if not user:
                content = f"**[Discord: {message.author.display_name}]**\n{content}"

            # Create the comment
            await sync_to_async(Comment.objects.create)(
                card=card,
                created_by=user,
                content=content
            )
            logger.debug(f"Synced message from {message.author} in thread {message.channel.id} to Card {card.id}")
            
        except Card.DoesNotExist:
            pass
        except Exception as e:
            logger.exception(f"Error syncing Discord message to Kanban comment: {e}")

    @discord.message_command(name="Upload to Ticket")
    async def upload_to_ticket(self, ctx: discord.ApplicationContext, message: discord.Message):
        # Check if we are in a ticket thread
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.respond("This action can only be used in a Ticket Thread.", ephemeral=True)
            return
            
        from .models import Card, Comment
        try:
            card = await sync_to_async(Card.objects.get)(discord_thread_id=ctx.channel.id)
            
            from allianceauth.services.modules.discord.models import DiscordUser
            discord_user = await sync_to_async(
                DiscordUser.objects.filter(uid=message.author.id).select_related('user').first
            )()
            user = discord_user.user if discord_user else None
            
            content = f"**[Uploaded from Discord - {message.author.display_name}]:**\n{message.content}"
            
            await sync_to_async(Comment.objects.create)(
                card=card,
                created_by=user,
                content=content
            )
            await ctx.respond(f"Message from {message.author.display_name} successfully uploaded as a comment to ticket #{card.id}.", ephemeral=True)
        except Card.DoesNotExist:
            await ctx.respond("This thread does not appear to be linked to a Kanban ticket.", ephemeral=True)
        except Exception as e:
            logger.exception(f"Error in upload_to_ticket context command: {e}")
            await ctx.respond("An error occurred while uploading the message.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(KanbanTicketCog(bot))
