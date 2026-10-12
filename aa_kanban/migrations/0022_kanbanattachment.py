# Generated for TASK-77

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aa_kanban", "0021_board_stale_card_repeat_hours_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="KanbanAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        help_text="Uploaded image or attachment file",
                        upload_to="aa_kanban/uploads/%Y/%m/",
                    ),
                ),
                (
                    "original_filename",
                    models.CharField(max_length=255),
                ),
                (
                    "size",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "uploader",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="kanban_attachments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Kanban Attachment",
                "verbose_name_plural": "Kanban Attachments",
                "ordering": ["-created_at"],
            },
        ),
    ]
