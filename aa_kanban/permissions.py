"""Permission helpers and decorators for aa_kanban."""

from functools import wraps
from typing import Callable

from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from .models import Board


def user_can_view_board(user: User | AnonymousUser, board: Board) -> bool:
    """Check if the user has permission to view the given board."""
    return board.can_user_view(user)


def user_can_write_board(user: User | AnonymousUser, board: Board) -> bool:
    """Check if the user has permission to modify/write to the given board."""
    return board.can_user_write(user)


def board_view_required(view_func: Callable) -> Callable:
    """Decorator for views requiring read access to a board.

    Expects 'board_slug' or 'board_id' in view kwargs.
    Injects resolved 'board' object into view kwargs.
    """

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")

        board = None
        if "board_slug" in kwargs:
            board = get_object_or_404(Board, slug=kwargs["board_slug"])
        elif "board_id" in kwargs:
            board = get_object_or_404(Board, pk=kwargs["board_id"])

        if board and not board.can_user_view(request.user):
            raise PermissionDenied("You do not have access to this board.")

        kwargs["board"] = board
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def board_write_required(view_func: Callable) -> Callable:
    """Decorator for views requiring mutation/write access to a board.

    Expects 'board_slug' or 'board_id' in view kwargs.
    Injects resolved 'board' object into view kwargs.
    """

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")

        board = None
        if "board_slug" in kwargs:
            board = get_object_or_404(Board, slug=kwargs["board_slug"])
        elif "board_id" in kwargs:
            board = get_object_or_404(Board, pk=kwargs["board_id"])

        if board and not board.can_user_write(request.user):
            raise PermissionDenied(
                "You do not have permission to modify this board."
            )

        kwargs["board"] = board
        return view_func(request, *args, **kwargs)

    return _wrapped_view
