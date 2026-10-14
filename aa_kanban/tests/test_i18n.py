"""Unit tests for internationalization (i18n) and bilingual support in aa-kanban."""

import pytest
from django.utils import translation
from django.utils.translation import gettext as _

from aa_kanban.models import Card


@pytest.mark.django_db
class TestBilingualTranslations:
    """Test bilingual (EN / NL) string translations across views and alerts."""

    def test_card_moved_webhook_bilingual(self):
        """Verify card moved notification formats correctly in EN and NL."""
        # 1. English
        with translation.override("en"):
            msg_en = _(
                "Card moved: **{card_title}** was moved from `{source_list_name}` to `{target_list_name}`.\n[View Board]({url})"
            ).format(
                card_title="Task Alpha",
                source_list_name="To Do",
                target_list_name="In Progress",
                url="http://example.com/board",
            )
            assert "[View Board](http://example.com/board)" in msg_en
            assert (
                "Card moved: **Task Alpha** was moved from `To Do` to `In Progress`."
                in msg_en
            )

        # 2. Dutch
        with translation.override("nl"):
            msg_nl = _(
                "Card moved: **{card_title}** was moved from `{source_list_name}` to `{target_list_name}`.\n[View Board]({url})"
            ).format(
                card_title="Task Alpha",
                source_list_name="To Do",
                target_list_name="In Progress",
                url="http://example.com/board",
            )
            assert "[Bekijk Bord](http://example.com/board)" in msg_nl
            assert (
                "Card verplaatst: **Task Alpha** is verplaatst van `To Do` naar `In Progress`."
                in msg_nl
            )

    def test_card_created_webhook_bilingual(self):
        """Verify card created notification formats correctly in EN and NL."""
        # 1. English
        with translation.override("en"):
            msg_en = _(
                "**New Card Created!**\nTitle: `{card_title}`\nCreated by: `{username}`\nList: `{list_name}`\n[View Board]({url})"
            ).format(
                card_title="New Feature",
                username="pilot1",
                list_name="Backlog",
                url="http://example.com/board",
            )
            assert "**New Card Created!**" in msg_en
            assert "Title: `New Feature`" in msg_en
            assert "[View Board](http://example.com/board)" in msg_en

        # 2. Dutch
        with translation.override("nl"):
            msg_nl = _(
                "**New Card Created!**\nTitle: `{card_title}`\nCreated by: `{username}`\nList: `{list_name}`\n[View Board]({url})"
            ).format(
                card_title="New Feature",
                username="pilot1",
                list_name="Backlog",
                url="http://example.com/board",
            )
            assert "**Nieuwe Card Aangemaakt!**" in msg_nl
            assert "Titel: `New Feature`" in msg_nl
            assert "[Bekijk Bord](http://example.com/board)" in msg_nl

    def test_board_created_message_bilingual(self):
        """Verify board created webhook message formats correctly in EN and NL."""
        # 1. English
        with translation.override("en"):
            msg_en = _(
                "**New Kanban Board Created!**\nName: `{board_name}`\nCreated by: `{username}`"
            ).format(board_name="Ops Board", username="commander")
            assert "**New Kanban Board Created!**" in msg_en
            assert "Name: `Ops Board`" in msg_en

        # 2. Dutch
        with translation.override("nl"):
            msg_nl = _(
                "**New Kanban Board Created!**\nName: `{board_name}`\nCreated by: `{username}`"
            ).format(board_name="Ops Board", username="commander")
            assert "**Nieuw Kanban Bord Aangemaakt!**" in msg_nl
            assert "Naam: `Ops Board`" in msg_nl

    def test_thread_closed_message_bilingual(self):
        """Verify thread close message formats correctly in EN and NL."""
        with translation.override("en"):
            msg_en = _(
                "🔒 This ticket has been marked as done and this thread is now closed."
            )
            assert "marked as done" in msg_en

        with translation.override("nl"):
            msg_nl = _(
                "🔒 This ticket has been marked as done and this thread is now closed."
            )
            assert "gemarkeerd als voltooid" in msg_nl

    def test_color_choices_bilingual(self):
        """Verify Card.COLOR_CHOICES display values translate in Dutch."""
        with translation.override("en"):
            colors_en = dict(Card.COLOR_CHOICES)
            assert str(colors_en["primary"]) == "Blue"
            assert str(colors_en["danger"]) == "Red"

        with translation.override("nl"):
            colors_nl = dict(Card.COLOR_CHOICES)
            assert str(colors_nl["primary"]) == "Blauw"
            assert str(colors_nl["danger"]) == "Rood"
