"""Return and reverse-logistics transitions for delivered orders."""

from django.db import transaction
from django.utils import timezone

from .inventory import restore_order_inventory
from .models import Order, Product, ReturnRequest, Shipment
from .payments import refund_payment


class ReturnNotAllowed(ValueError):
    pass


class ReturnTransitionError(ValueError):
    pass


def order_can_be_returned(order):
    """Return whether an order is eligible to enter the return workflow."""

    has_physical_item = order.items.filter(
        product_type__in=[Product.PHYSICAL, Product.HYBRID]
    ).exists()
    shipment_is_delivered = (
        hasattr(order, "shipment") and order.shipment.status == Shipment.DELIVERED
    )
    return (
        order.status == Order.COMPLETED
        and order.payment_status == Order.PAYMENT_PAID
        and has_physical_item
        and shipment_is_delivered
        and not ReturnRequest.objects.filter(order=order).exists()
    )


def request_order_return(order, reason):
    reason = reason.strip()
    if not reason:
        raise ReturnNotAllowed("Please explain why you are returning the order.")

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        existing = ReturnRequest.objects.filter(order=order).first()
        if existing:
            return existing
        if not order_can_be_returned(order):
            raise ReturnNotAllowed(
                "Only paid, delivered physical orders can be returned."
            )
        return ReturnRequest.objects.create(order=order, reason=reason)


def approve_return(return_request, notes=""):
    with transaction.atomic():
        return_request = ReturnRequest.objects.select_for_update().get(
            pk=return_request.pk
        )
        if return_request.status == ReturnRequest.APPROVED:
            return return_request
        if return_request.status != ReturnRequest.REQUESTED:
            raise ReturnTransitionError("Only requested returns can be approved.")
        return_request.status = ReturnRequest.APPROVED
        return_request.review_notes = notes.strip()
        return_request.pickup_provider = "manual"
        return_request.pickup_reference = f"DEMO-RETURN-{return_request.order_id:06d}"
        return_request.tracking_number = return_request.pickup_reference
        return_request.reviewed_at = timezone.now()
        return_request.save(
            update_fields=[
                "status",
                "review_notes",
                "pickup_provider",
                "pickup_reference",
                "tracking_number",
                "reviewed_at",
                "updated_at",
            ]
        )
        return return_request


def reject_return(return_request, notes=""):
    with transaction.atomic():
        return_request = ReturnRequest.objects.select_for_update().get(
            pk=return_request.pk
        )
        if return_request.status == ReturnRequest.REJECTED:
            return return_request
        if return_request.status != ReturnRequest.REQUESTED:
            raise ReturnTransitionError("Only requested returns can be rejected.")
        return_request.status = ReturnRequest.REJECTED
        return_request.review_notes = notes.strip()
        return_request.reviewed_at = timezone.now()
        return_request.save(
            update_fields=["status", "review_notes", "reviewed_at", "updated_at"]
        )
        return return_request


def mark_return_in_transit(return_request):
    with transaction.atomic():
        return_request = ReturnRequest.objects.select_for_update().get(
            pk=return_request.pk
        )
        if return_request.status == ReturnRequest.IN_TRANSIT:
            return return_request
        if return_request.status != ReturnRequest.APPROVED:
            raise ReturnTransitionError("Approve the return before pickup.")
        return_request.status = ReturnRequest.IN_TRANSIT
        return_request.save(update_fields=["status", "updated_at"])
        return return_request


def mark_return_received(return_request):
    with transaction.atomic():
        return_request = ReturnRequest.objects.select_for_update().get(
            pk=return_request.pk
        )
        if return_request.status == ReturnRequest.RECEIVED:
            return return_request
        if return_request.status not in {
            ReturnRequest.APPROVED,
            ReturnRequest.IN_TRANSIT,
        }:
            raise ReturnTransitionError("This return is not ready to be received.")
        return_request.status = ReturnRequest.RECEIVED
        return_request.received_at = timezone.now()
        return_request.save(update_fields=["status", "received_at", "updated_at"])
        return return_request


def complete_return(return_request):
    """Refund a received return and restore inventory exactly once."""

    with transaction.atomic():
        return_request = ReturnRequest.objects.select_for_update().select_related(
            "order"
        ).get(pk=return_request.pk)
        if return_request.status == ReturnRequest.REFUNDED:
            return return_request
        if return_request.status != ReturnRequest.RECEIVED:
            raise ReturnTransitionError("Receive and inspect the return before refunding.")

        order = Order.objects.select_for_update().get(pk=return_request.order_id)
        refund_reference = refund_payment(order)
        restore_order_inventory(order)

        order.status = Order.RETURNED
        order.payment_status = Order.PAYMENT_REFUNDED
        order.fulfillment_status = Order.FULFILLMENT_RETURNED
        order.refund_reference = refund_reference
        order.refunded_at = timezone.now()
        order.save(
            update_fields=[
                "status",
                "payment_status",
                "fulfillment_status",
                "refund_reference",
                "refunded_at",
                "updated_at",
            ]
        )
        return_request.status = ReturnRequest.REFUNDED
        return_request.completed_at = timezone.now()
        return_request.save(update_fields=["status", "completed_at", "updated_at"])
        return return_request
