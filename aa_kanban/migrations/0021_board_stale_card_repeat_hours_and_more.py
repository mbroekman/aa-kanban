# Generated for TASK-80

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aa_kanban", "0020_kanbanteam_groups"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="stale_card_repeat_hours",
            field=models.PositiveIntegerField(
                default=24,
                help_text="Hours between reminder alerts for a still inactive card (0 for one-time alert only).",
            ),
        ),
        migrations.AddField(
            model_name="card",
            name="last_stale_alert_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Timestamp when the last stale card alert was sent for this card.",
                null=True,
            ),
        ),
    ]
