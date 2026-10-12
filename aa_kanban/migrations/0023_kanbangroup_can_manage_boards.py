# Generated manually for TASK-84

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aa_kanban", "0022_kanbanattachment"),
    ]

    operations = [
        migrations.AddField(
            model_name="kanbangroup",
            name="can_manage_boards",
            field=models.BooleanField(
                default=False,
                help_text="Members of this group can manage Kanban settings and boards.",
            ),
        ),
    ]
