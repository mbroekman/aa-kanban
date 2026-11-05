from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aa_kanban", "0026_intakeapikey"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="is_members_board",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Show this board on the members page instead of the management "
                    "dashboard. Everyone with Kanban access can view it; only its "
                    "write groups can change it."
                ),
            ),
        ),
        migrations.AddField(
            model_name="board",
            name="is_archived",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "An archived board is hidden from the dashboards and read-only. "
                    "Only board managers can open and restore it."
                ),
            ),
        ),
        migrations.AddField(
            model_name="board",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="kanbansetting",
            name="members_page_name",
            field=models.CharField(
                default="Member Boards",
                help_text="Name of the members page in the Auth menu.",
                max_length=50,
            ),
        ),
    ]
