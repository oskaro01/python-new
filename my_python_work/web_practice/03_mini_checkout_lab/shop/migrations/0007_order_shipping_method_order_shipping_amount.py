from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0006_product_product_type_orderitem_product_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="shipping_method",
            field=models.CharField(default="", max_length=30),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
