"""Unit tests for aa_kanban models."""

import pytest
from django.contrib.auth.models import AnonymousUser, User
from aa_kanban.models import KanbanGroup as Group

from aa_kanban.models import Board, Card, Comment, Label, List


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
def board_factory(db, user_factory):
    def create_board(name="Test Board", created_by=None, **kwargs):
        if created_by is None:
            created_by = user_factory(f"creator_{Board.objects.count()}")
        return Board.objects.create(name=name, created_by=created_by, **kwargs)
    return create_board


@pytest.mark.django_db
class TestBoardModel:
    def test_board_creation_and_str(self, board_factory):
        board = board_factory(name="Operations Board")
        assert str(board) == "Operations Board"
        assert board.slug == "operations-board"

    def test_board_slug_collision(self, board_factory):
        board1 = board_factory(name="Fleet Board")
        board2 = board_factory(name="Fleet Board")
        assert board1.slug == "fleet-board"
        assert board2.slug == "fleet-board-1"

    def test_can_user_view(self, board_factory, user_factory, group_factory):
        board = board_factory(name="Secret Board")
        view_grp = group_factory("Viewers")
        write_grp = group_factory("Editors")
        board.view_groups.add(view_grp)
        board.write_groups.add(write_grp)

        unauth = AnonymousUser()
        assert board.can_user_view(unauth) is False

        random_user = user_factory("random")
        assert board.can_user_view(random_user) is False

        viewer = user_factory("viewer")
        viewer.kanban_groups.add(view_grp)
        assert board.can_user_view(viewer) is True

        editor = user_factory("editor")
        editor.kanban_groups.add(write_grp)
        assert board.can_user_view(editor) is True

        superuser = user_factory("superadmin", is_superuser=True)
        assert board.can_user_view(superuser) is True

        assert board.can_user_view(board.created_by) is True

    def test_can_user_write(self, board_factory, user_factory, group_factory):
        board = board_factory(name="Project Alpha")
        view_grp = group_factory("Viewers Alpha")
        write_grp = group_factory("Editors Alpha")
        board.view_groups.add(view_grp)
        board.write_groups.add(write_grp)

        unauth = AnonymousUser()
        assert board.can_user_write(unauth) is False

        random_user = user_factory("random_alpha")
        assert board.can_user_write(random_user) is False

        viewer = user_factory("viewer_alpha")
        viewer.kanban_groups.add(view_grp)
        assert board.can_user_write(viewer) is False

        editor = user_factory("editor_alpha")
        editor.kanban_groups.add(write_grp)
        assert board.can_user_write(editor) is True

        superuser = user_factory("superadmin_alpha", is_superuser=True)
        assert board.can_user_write(superuser) is True

        assert board.can_user_write(board.created_by) is True

    def test_board_queryset_visible_to(
        self, board_factory, user_factory, group_factory
    ):
        creator = user_factory("master_creator")
        user = user_factory("normal_user")
        grp = group_factory("Group A")
        user.kanban_groups.add(grp)

        b1 = board_factory(name="Public to Group A", created_by=creator)
        b1.view_groups.add(grp)

        b2 = board_factory(name="Private to Creator", created_by=creator)

        b3 = board_factory(name="User Owns This", created_by=user)

        visible = Board.objects.visible_to(user)
        assert b1 in visible
        assert b2 not in visible
        assert b3 in visible

        assert Board.objects.visible_to(AnonymousUser()).count() == 0


@pytest.mark.django_db
class TestListAndCardModels:
    def test_list_and_card_creation_and_ordering(self, board_factory, user_factory):
        board = board_factory(name="Dev Board")
        list1 = List.objects.create(board=board, name="To Do", order=1)
        list2 = List.objects.create(board=board, name="In Progress", order=0)

        # Lists ordered by order, id
        assert list(board.lists.all()) == [list2, list1]
        assert str(list1) == "Dev Board - To Do"

        card1 = Card.objects.create(list=list1, title="Task 1", order=2)
        card2 = Card.objects.create(list=list1, title="Task 2", order=1)
        assert list(list1.cards.all()) == [card2, card1]
        assert str(card1) == "Task 1"

        # Assignees
        dev = user_factory("developer")
        card1.assignees.add(dev)
        assert dev in card1.assignees.all()

    def test_cascade_deletion(self, board_factory):
        board = board_factory(name="Temporary Board")
        lst = List.objects.create(board=board, name="Column")
        card = Card.objects.create(list=lst, title="Temporary Card")
        label = Label.objects.create(board=board, name="Bug", color="danger")
        card.labels.add(label)

        assert List.objects.filter(pk=lst.pk).exists()
        assert Card.objects.filter(pk=card.pk).exists()
        assert Label.objects.filter(pk=label.pk).exists()

        board.delete()

        assert not List.objects.filter(pk=lst.pk).exists()
        assert not Card.objects.filter(pk=card.pk).exists()
        assert not Label.objects.filter(pk=label.pk).exists()


@pytest.mark.django_db
class TestLabelAndCommentModels:
    def test_label_and_comment(self, board_factory, user_factory):
        board = board_factory(name="Scrum Board")
        lst = List.objects.create(board=board, name="Backlog")
        card = Card.objects.create(list=lst, title="Feature X")
        label = Label.objects.create(board=board, name="Enhancement", color="info")
        card.labels.add(label)

        assert str(label) == "Enhancement (info)"
        assert label in card.labels.all()

        author = user_factory("commenter")
        comment = Comment.objects.create(
            card=card, author=author, text="This looks good!"
        )
        assert str(comment) == f"Comment by {author} on {card.title}"
        assert comment in card.comments.all()
