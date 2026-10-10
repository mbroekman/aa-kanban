# Generated manually for TASK-74

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('aa_kanban', '0019_board_stale_card_alert_hours_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='kanbanteam',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                help_text='Auth groups that belong to this team.',
                related_name='kanban_ticket_teams',
                to='auth.group',
            ),
        ),
    ]
