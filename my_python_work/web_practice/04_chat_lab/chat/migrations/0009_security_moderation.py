import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0008_message_expiry"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("blocked", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocks_received", to=settings.AUTH_USER_MODEL)),
                ("blocker", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocks_created", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("blocker", "blocked"), name="unique_user_block"),
                    models.CheckConstraint(condition=~Q(("blocker", models.F("blocked"))), name="user_blocks_different_users"),
                ],
            },
        ),
        migrations.CreateModel(
            name="MessageReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.CharField(choices=[("spam", "Spam"), ("harassment", "Harassment"), ("threat", "Threat"), ("other", "Other")], max_length=20)),
                ("status", models.CharField(choices=[("open", "Open"), ("reviewed", "Reviewed"), ("dismissed", "Dismissed")], default="open", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("message", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reports", to="chat.message")),
                ("reporter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="message_reports", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [models.UniqueConstraint(fields=("message", "reporter"), name="unique_message_reporter")],
            },
        ),
    ]
