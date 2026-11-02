from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aa_kanban", "0025_comment_author_nullable"),
    ]

    operations = [
        migrations.CreateModel(
            name="IntakeApiKey",
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
                    "name",
                    models.CharField(
                        help_text="Who or what uses this key.", max_length=100
                    ),
                ),
                (
                    "key_hash",
                    models.CharField(editable=False, max_length=64, unique=True),
                ),
                (
                    "prefix",
                    models.CharField(
                        editable=False,
                        help_text="First characters of the key, to recognise it.",
                        max_length=8,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "last_used_at",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
            ],
            options={
                "verbose_name": "Intake API key",
                "verbose_name_plural": "Intake API keys",
                "ordering": ["name"],
            },
        ),
    ]
