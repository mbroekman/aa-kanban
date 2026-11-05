from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aa_kanban", "0027_board_archive_members_page"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="own_cards_only",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Readers only see the cards they created or are assigned to, "
                    "and can add cards in the first column. Write groups and board "
                    "managers see all cards."
                ),
            ),
        ),
    ]
