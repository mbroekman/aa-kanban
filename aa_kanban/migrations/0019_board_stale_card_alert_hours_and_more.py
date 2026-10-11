# Generated manually for TASK-72

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aa_kanban", "0018_label_is_ticket_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="discord_alert_channel_id",
            field=models.BigIntegerField(
                blank=True,
                help_text="Discord Channel ID for stale card alerts. If blank, falls back to ticket channel.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="board",
            name="discord_alert_webhook",
            field=models.URLField(
                blank=True,
                help_text="Discord Webhook URL for stale card alerts. If blank, falls back to card movement webhook.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="board",
            name="stale_card_alert_hours",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Hours of inactivity after which cards trigger an alert (0 to disable).",
            ),
        ),
    ]
