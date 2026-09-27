import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def move_category_text_to_models(apps, schema_editor):
    Category = apps.get_model("dictionary", "Category")
    Word = apps.get_model("dictionary", "Word")

    for word in Word.objects.exclude(category_text="").iterator():
        name = word.category_text.strip()
        if not name:
            continue

        category = Category.objects.filter(
            owner_id=word.owner_id,
            name__iexact=name,
        ).first()
        if category is None:
            category = Category.objects.create(owner_id=word.owner_id, name=name)

        word.category_id = category.pk
        word.save(update_fields=["category"])


def restore_category_text(apps, schema_editor):
    Word = apps.get_model("dictionary", "Word")

    for word in Word.objects.exclude(category=None).select_related("category").iterator():
        word.category_text = word.category.name
        word.save(update_fields=["category_text"])


class Migration(migrations.Migration):
    dependencies = [
        ("dictionary", "0002_word_owner"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="word",
            old_name="category",
            new_name="category_text",
        ),
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=60)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="word_categories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                fields=("owner", "name"),
                name="unique_owner_category",
            ),
        ),
        migrations.AddField(
            model_name="word",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="words",
                to="dictionary.category",
            ),
        ),
        migrations.RunPython(move_category_text_to_models, restore_category_text),
        migrations.RemoveField(
            model_name="word",
            name="category_text",
        ),
    ]
