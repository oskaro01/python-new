from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_order_receipt_sent_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="product_type",
            field=models.CharField(
                choices=[
                    ("physical", "Physical"),
                    ("digital", "Digital"),
                    ("hybrid", "Physical + digital"),
                ],
                default="physical",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="product_type",
            field=models.CharField(
                choices=[
                    ("physical", "Physical"),
                    ("digital", "Digital"),
                    ("hybrid", "Physical + digital"),
                ],
                default="physical",
                max_length=20,
            ),
        ),
    ]
