from datetime import timedelta

import chat.models
from django.db import migrations, models


def backfill_message_expiry(apps, schema_editor):
    # Existing messages receive 24 hours from their original creation time.
    # Avoid rewriting their history based on when this migration is applied.
    Message = apps.get_model("chat", "Message")
    batch = []
    queryset = Message.objects.using(schema_editor.connection.alias).all()
    for message in queryset.iterator(chunk_size=500):
        message.expires_at = message.created_at + timedelta(hours=24)
        batch.append(message)
        if len(batch) == 500:
            queryset.bulk_update(batch, ["expires_at"], batch_size=500)
            batch.clear()
    if batch:
        queryset.bulk_update(batch, ["expires_at"], batch_size=500)


class Migration(migrations.Migration):
    dependencies = [("chat", "0007_messageattachment_expires_at")]

    operations = [
        migrations.AddField(
            model_name="message",
            name="expires_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(backfill_message_expiry, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="message",
            name="expires_at",
            field=models.DateTimeField(default=chat.models.default_message_expiry, db_index=True),
        ),
        migrations.AlterField(
            model_name="messageattachment",
            name="expires_at",
            field=models.DateTimeField(default=chat.models.default_attachment_expiry, db_index=True),
        ),
    ]
