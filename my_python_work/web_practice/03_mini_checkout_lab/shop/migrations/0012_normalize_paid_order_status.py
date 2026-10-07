from django.db import migrations


def normalize_paid_order_status(apps, schema_editor):
    Order = apps.get_model("shop", "Order")
    Order.objects.filter(
        payment_status="paid",
        fulfillment_status="delivered",
    ).update(status="completed")
    Order.objects.filter(payment_status="paid").exclude(
        fulfillment_status="delivered"
    ).update(status="processing")


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0011_alter_order_status"),
    ]

    operations = [
        migrations.RunPython(
            normalize_paid_order_status,
            migrations.RunPython.noop,
        ),
    ]
