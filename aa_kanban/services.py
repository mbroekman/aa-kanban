"""
Service layer for aa-kanban.

This module provides the official Python API for external plugins (like aa-industry)
to safely interact with Kanban boards, lists, and cards without bypassing core business logic
like discord webhook notifications or permission checks.
"""

from typing import Optional, List as TypingList
from django.contrib.auth.models import User

from .models import Board, List, Card, KanbanSetting, Label


def create_kanban_board(
    name: str, 
    creator: User, 
    description: str = "", 
    view_group_ids: Optional[TypingList[int]] = None,
    write_group_ids: Optional[TypingList[int]] = None
) -> Board:
    """
    Safely create a new Kanban Board.
    """
    board = Board.objects.create(
        name=name,
        description=description,
        created_by=creator,
    )
    
    if view_group_ids:
        board.view_groups.set(view_group_ids)
    if write_group_ids:
        board.write_groups.set(write_group_ids)

    # Trigger Discord Webhook Notification if configured
    settings = KanbanSetting.get_settings()
    if settings.board_creation_webhook:
        from aa_kanban.utils import send_discord_webhook
        message = f"**New Kanban Board Created!**\nName: `{board.name}`\nCreated by: `{creator.username}`"
        send_discord_webhook(settings.board_creation_webhook, message)

    return board


def create_kanban_card(
    board_id: int, 
    title: str, 
    creator: User, 
    description: str = "", 
    column_name: str = "Backlog",
    label_ids: Optional[TypingList[int]] = None
) -> Card:
    """
    Safely create a new Kanban Card in a specific board and column.
    If the column does not exist, it falls back to the first available column.
    """
    board = Board.objects.get(pk=board_id)
    
    # Find the target list/column by name (case-insensitive) or fallback to first
    lst = board.lists.filter(name__iexact=column_name).first() or board.lists.first()
    
    if not lst:
        raise ValueError("Cannot create card: The target board has no columns.")
    
    card = Card.objects.create(
        list=lst,
        title=title,
        description=description,
        created_by=creator
    )
    
    if label_ids:
        card.labels.set(label_ids)

    # Trigger Discord Webhook Notification if configured for this board
    if board.discord_webhook_cards:
        from aa_kanban.utils import send_discord_webhook
        msg = f"**New Ticket Submitted!**\nTitle: `{card.title}`\nCreated by: `{creator.username}`\nBoard: `{board.name}`"
        send_discord_webhook(board.discord_webhook_cards, msg)
        
    return card


def move_kanban_card(card_id: int, target_column_name: str) -> Card:
    """
    Move an existing card to a different column in the same board.
    """
    card = Card.objects.select_related('list__board').get(pk=card_id)
    board = card.list.board
    
    target_list = board.lists.filter(name__iexact=target_column_name).first()
    if not target_list:
        raise ValueError(f"Target column '{target_column_name}' does not exist on this board.")
        
    card.list = target_list
    card.save(update_fields=['list', 'updated_at'])
    return card
