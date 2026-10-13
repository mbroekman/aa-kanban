# Generated manually for TASK-95

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aa_kanban", "0023_kanbangroup_can_manage_boards"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="archive_after_days",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Days a card may sit in the last list before auto-archiving (0 to disable).",
            ),
        ),
        migrations.AddField(
            model_name="card",
            name="moved_to_list_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text="When the card most recently entered its current list.",
            ),
        ),
        migrations.AddField(
            model_name="card",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="card",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
