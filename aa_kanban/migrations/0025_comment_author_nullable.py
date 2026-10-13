# Generated manually for TASK-96

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("aa_kanban", "0024_card_archiving_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="author",
            field=models.ForeignKey(
                blank=True,
                help_text="Null when posted by a Discord user with no linked Alliance Auth account.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="kanban_comments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
