from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dictionary", "0006_remove_word_is_favorite"),
    ]

    operations = [
        migrations.AddField(
            model_name="word",
            name="focus_first",
            field=models.BooleanField(
                default=False,
                help_text="Show this word before the rest of your dictionary.",
            ),
        ),
    ]
