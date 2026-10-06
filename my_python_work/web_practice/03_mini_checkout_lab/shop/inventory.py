"""Inventory changes that happen after verified payment."""

from django.db import transaction
from django.utils import timezone

from .models import Order, Product


def deduct_paid_order_inventory(order):
    """Deduct physical stock once, with row locks protecting the check."""

    if order.inventory_status == Order.INVENTORY_DEDUCTED:
        return True

    items = list(order.items.select_related("product").all())
    physical_items = [
        item
        for item in items
        if item.product_type in {Product.PHYSICAL, Product.HYBRID}
    ]
    if not physical_items:
        order.inventory_status = Order.INVENTORY_NOT_REQUIRED
        order.save(update_fields=["inventory_status", "updated_at"])
        return True

    with transaction.atomic():
        product_ids = {item.product_id for item in physical_items}
        locked_products = {
            product.pk: product
            for product in Product.objects.select_for_update().filter(
                pk__in=product_ids
            )
        }

        if any(
            item.product_id not in locked_products
            or locked_products[item.product_id].stock < item.quantity
            for item in physical_items
        ):
            order.inventory_status = Order.INVENTORY_UNAVAILABLE
            order.save(update_fields=["inventory_status", "updated_at"])
            return False

        for item in physical_items:
            product = locked_products[item.product_id]
            product.stock -= item.quantity
            product.save(update_fields=["stock", "updated_at"])

        order.inventory_status = Order.INVENTORY_DEDUCTED
        order.inventory_deducted_at = timezone.now()
        order.save(
            update_fields=[
                "inventory_status",
                "inventory_deducted_at",
                "updated_at",
            ]
        )
        return True
