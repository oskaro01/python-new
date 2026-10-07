"""Cancellation and refund transitions for orders."""

from django.db import transaction
from django.utils import timezone

from .inventory import restore_cancelled_order_inventory
from .models import Order, Shipment
from .payments import refund_payment


class CancellationNotAllowed(ValueError):
    pass


def cancel_order(order, reason=""):
    """Cancel an order once, refunding paid orders and restoring stock."""

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.status == Order.CANCELLED:
            return order
        if order.status == Order.COMPLETED:
            raise CancellationNotAllowed("Completed orders cannot be cancelled.")
        if hasattr(order, "shipment"):
            raise CancellationNotAllowed("Shipped orders must use a return workflow.")

        refund_reference = ""
        if order.payment_status == Order.PAYMENT_PAID:
            refund_reference = refund_payment(order)
        elif order.payment_status not in {
            Order.PAYMENT_PENDING,
            Order.PAYMENT_FAILED,
        }:
            raise CancellationNotAllowed("This order cannot be cancelled now.")

        restore_cancelled_order_inventory(order)
        order.status = Order.CANCELLED
        if refund_reference:
            order.payment_status = Order.PAYMENT_REFUNDED
            order.refund_reference = refund_reference
            order.refunded_at = timezone.now()
        if reason:
            order.notes = f"{order.notes}\nCancellation: {reason}".strip()
        update_fields = ["status", "notes", "updated_at"]
        if refund_reference:
            update_fields.extend(["payment_status", "refund_reference", "refunded_at"])
        order.save(update_fields=update_fields)
        return order
