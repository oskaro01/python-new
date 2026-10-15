from datetime import timedelta

from django.db import migrations


SHORT_TTL = timedelta(seconds=300)


def shorten_existing_expiry(apps, schema_editor):
    Message = apps.get_model("chat", "Message")
    MessageAttachment = apps.get_model("chat", "MessageAttachment")
    database = schema_editor.connection.alias

    for model in (Message, MessageAttachment):
        rows = model.objects.using(database).all().iterator(chunk_size=500)
        batch = []
        for row in rows:
            shortened_deadline = row.created_at + SHORT_TTL
            if row.expires_at > shortened_deadline:
                row.expires_at = shortened_deadline
                batch.append(row)
            if len(batch) == 500:
                model.objects.using(database).bulk_update(batch, ["expires_at"], batch_size=500)
                batch.clear()
        if batch:
            model.objects.using(database).bulk_update(batch, ["expires_at"], batch_size=500)


class Migration(migrations.Migration):
    dependencies = [("chat", "0009_security_moderation")]

    operations = [
        migrations.RunPython(shorten_existing_expiry, migrations.RunPython.noop),
    ]
