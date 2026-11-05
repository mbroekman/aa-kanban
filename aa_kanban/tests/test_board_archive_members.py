"""Board archiving (TASK-109) and the members page (TASK-110)."""

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.test import Client, RequestFactory
from django.urls import reverse

from aa_kanban.auth_hooks import AaKanbanMembersMenuItem
from aa_kanban.models import Board, KanbanGroup, KanbanSetting


def member(username, *perms):
    user = AuthUtils.create_user(username)
    AuthUtils.add_main_character(
        user, username, character_id=abs(hash(username)) % 10**8
    )
    AuthUtils.add_permission_to_user_by_name("aa_kanban.basic_access", user)
    for perm in perms:
        AuthUtils.add_permission_to_user_by_name(perm, user)
    return user


def client_for(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def people(db):
    manager = member("manager", "aa_kanban.manage_boards")
    writer = member("writer")
    reader = member("reader")
    writers = KanbanGroup.objects.create(name="Writers")
    writers.members.add(writer)
    return {"manager": manager, "writer": writer, "reader": reader, "writers": writers}


@pytest.mark.django_db
class TestArchiveBoard:
    def test_archive_hides_board_and_makes_it_read_only(self, people):
        board = Board.objects.create(name="Ops", created_by=people["manager"])
        board.write_groups.add(people["writers"])

        response = client_for(people["manager"]).post(
            reverse("aa_kanban:archive_board", args=[board.slug])
        )

        assert response.status_code == 302
        board.refresh_from_db()
        assert board.is_archived and board.archived_at
        assert not board.can_user_write(people["writer"])
        assert not board.can_user_write(people["manager"])
        index = client_for(people["writer"]).get(reverse("aa_kanban:index"))
        assert board not in list(index.context["boards"])

    def test_only_managers_open_an_archived_board(self, people):
        board = Board.objects.create(name="Ops", is_archived=True)
        board.write_groups.add(people["writers"])
        url = reverse("aa_kanban:board_detail", args=[board.slug])

        assert client_for(people["writer"]).get(url).status_code == 403
        page = client_for(people["manager"]).get(url)
        assert page.status_code == 200
        assert "Restore Board" in page.content.decode()

    def test_archived_boards_page_and_restore(self, people):
        board = Board.objects.create(name="Old Ops", is_archived=True)
        manager = client_for(people["manager"])

        listing = manager.get(reverse("aa_kanban:archived_boards"))
        assert list(listing.context["boards"]) == [board]
        assert manager.get(reverse("aa_kanban:index")).context["archived_count"] == 1

        manager.post(
            reverse("aa_kanban:restore_board", args=[board.slug]),
            HTTP_HX_REQUEST="true",
        )
        board.refresh_from_db()
        assert not board.is_archived and board.archived_at is None

    def test_non_admins_cannot_archive_or_see_the_archive(self, people):
        board = Board.objects.create(name="Ops")
        board.write_groups.add(people["writers"])
        writer = client_for(people["writer"])

        assert (
            writer.post(
                reverse("aa_kanban:archive_board", args=[board.slug])
            ).status_code
            == 403
        )
        assert writer.get(reverse("aa_kanban:archived_boards")).status_code == 403
        assert (
            writer.get(
                reverse("aa_kanban:archive_board", args=[board.slug])
            ).status_code
            == 405
        )

    def test_archived_board_gets_no_stale_alerts(self, people):
        board = Board.objects.create(
            name="Ops", stale_card_alert_hours=1, is_archived=True
        )
        assert not board.get_stale_cards().exists()

    def test_archived_ticket_board_leaves_the_ticket_form(self, people):
        AuthUtils.add_permission_to_user_by_name(
            "aa_kanban.create_ticket", people["reader"]
        )
        Board.objects.create(name="Tickets", is_ticket_board=True, is_archived=True)

        response = client_for(people["reader"]).get(reverse("aa_kanban:create_ticket"))

        assert "No ticket boards are configured" in response.content.decode()


@pytest.mark.django_db
class TestMembersPage:
    def test_members_board_is_on_members_page_only(self, people):
        shared = Board.objects.create(name="Corp Events", is_members_board=True)
        Board.objects.create(
            name="Archived Event", is_members_board=True, is_archived=True
        )
        reader = client_for(people["reader"])

        members = reader.get(reverse("aa_kanban:members_index"))
        index = reader.get(reverse("aa_kanban:index"))
        summary = reader.get(reverse("aa_kanban:summary"))

        assert [b.name for b in members.context["boards"]] == ["Corp Events"]
        assert shared not in list(index.context["boards"])
        assert shared not in list(summary.context["boards"])

    def test_everyone_with_access_views_but_only_write_groups_change(self, people):
        board = Board.objects.create(name="Corp Events", is_members_board=True)
        board.write_groups.add(people["writers"])

        assert board.can_user_view(people["reader"])
        assert not board.can_user_write(people["reader"])
        assert board.can_user_write(people["writer"])
        url = reverse("aa_kanban:board_detail", args=[board.slug])
        assert client_for(people["reader"]).get(url).status_code == 200

    def test_no_basic_access_no_members_board(self, db):
        outsider = AuthUtils.create_user("outsider")
        board = Board.objects.create(name="Corp Events", is_members_board=True)
        assert not board.can_user_view(outsider)
        assert board not in Board.objects.visible_to(outsider)

    def test_board_form_sets_members_flag(self, people):
        board = Board.objects.create(name="Ops", created_by=people["manager"])
        client_for(people["manager"]).post(
            reverse("aa_kanban:edit_board", args=[board.slug]),
            {"name": "Ops", "is_members_board": "on"},
        )
        board.refresh_from_db()
        assert board.is_members_board

    def test_menu_item_uses_setting_name_and_needs_a_members_board(self, people):
        request = RequestFactory().get("/")
        request.user = people["reader"]
        item = AaKanbanMembersMenuItem()

        assert item.render(request) == ""

        Board.objects.create(name="Corp Events", is_members_board=True)
        settings = KanbanSetting.get_settings()
        settings.members_page_name = "Corp Boards"
        settings.save()

        assert "Corp Boards" in item.render(request)

    def test_settings_form_renames_the_members_page(self, people):
        response = client_for(people["manager"]).post(
            reverse("aa_kanban:update_global_settings"),
            {"members_page_name": "  Alliance Boards  "},
        )

        assert response.status_code == 302
        assert response.url.endswith("#general")
        assert KanbanSetting.get_settings().members_page_name == "Alliance Boards"

    def test_settings_form_rejects_an_empty_name(self, people):
        client_for(people["manager"]).post(
            reverse("aa_kanban:update_global_settings"), {"members_page_name": " "}
        )
        assert KanbanSetting.get_settings().members_page_name == "Member Boards"
