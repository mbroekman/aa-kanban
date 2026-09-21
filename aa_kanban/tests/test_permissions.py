"""Tests for aa_kanban permissions and decorators."""

import pytest
from django.contrib.auth.models import AnonymousUser, User
from aa_kanban.models import KanbanGroup as Group
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory

from aa_kanban.models import Board
from aa_kanban.permissions import board_view_required, board_write_required


@pytest.fixture
def user_factory(db):
    def create_user(username, **kwargs):
        return User.objects.create_user(
            username=username, email=f"{username}@example.com", **kwargs
        )
    return create_user


@pytest.fixture
def group_factory(db):
    def create_group(name):
        return Group.objects.create(name=name)
    return create_group


@pytest.fixture
def test_board(db, user_factory, group_factory):
    creator = user_factory("board_creator")
    board = Board.objects.create(name="Perm Board", created_by=creator)
    v_group = group_factory("View Group")
    w_group = group_factory("Write Group")
    board.view_groups.add(v_group)
    board.write_groups.add(w_group)
    return board, v_group, w_group


@board_view_required
def dummy_view(request, board_slug, board):
    return HttpResponse(f"View OK: {board.name}")


@board_write_required
def dummy_write_view(request, board_slug, board):
    return HttpResponse(f"Write OK: {board.name}")


@pytest.mark.django_db
class TestPermissionDecorators:
    def test_board_view_unauthenticated(self, test_board):
        board, _, _ = test_board
        factory = RequestFactory()
        request = factory.get(f"/board/{board.slug}/")
        request.user = AnonymousUser()

        with pytest.raises(PermissionDenied):
            dummy_view(request, board_slug=board.slug)

    def test_board_view_no_group(self, test_board, user_factory):
        board, _, _ = test_board
        user = user_factory("unauth_user")
        factory = RequestFactory()
        request = factory.get(f"/board/{board.slug}/")
        request.user = user

        with pytest.raises(PermissionDenied):
            dummy_view(request, board_slug=board.slug)

    def test_board_view_with_view_group(self, test_board, user_factory):
        board, v_group, _ = test_board
        user = user_factory("viewer_user")
        user.kanban_groups.add(v_group)

        factory = RequestFactory()
        request = factory.get(f"/board/{board.slug}/")
        request.user = user

        response = dummy_view(request, board_slug=board.slug)
        assert response.status_code == 200
        assert b"View OK" in response.content

    def test_board_write_denied_for_view_only_user(
        self, test_board, user_factory
    ):
        board, v_group, _ = test_board
        user = user_factory("readonly_user")
        user.kanban_groups.add(v_group)

        factory = RequestFactory()
        request = factory.post(f"/board/{board.slug}/mutate/")
        request.user = user

        with pytest.raises(PermissionDenied):
            dummy_write_view(request, board_slug=board.slug)

    def test_board_write_allowed_for_write_group(
        self, test_board, user_factory
    ):
        board, _, w_group = test_board
        user = user_factory("writer_user")
        user.kanban_groups.add(w_group)

        factory = RequestFactory()
        request = factory.post(f"/board/{board.slug}/mutate/")
        request.user = user

        response = dummy_write_view(request, board_slug=board.slug)
        assert response.status_code == 200
        assert b"Write OK" in response.content
