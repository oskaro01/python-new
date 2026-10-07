"""Shipping rates and the courier-provider boundary for fulfillment."""

from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Order, Shipment


SHIPPING_METHODS = {
    "standard": {
        "label": "Standard delivery (3-7 business days)",
        "amount": Decimal("5.00"),
    },
    "express": {
        "label": "Express delivery (1-2 business days)",
        "amount": Decimal("12.00"),
    },
}


def shipping_choices():
    return [
        (key, f"{details['label']} - ${details['amount']:.2f}")
        for key, details in SHIPPING_METHODS.items()
    ]


def shipping_cost(method):
    return SHIPPING_METHODS[method]["amount"]


@dataclass(frozen=True)
class ShipmentResult:
    provider: str
    provider_reference: str
    tracking_number: str
    tracking_url: str = ""
    payload: dict | None = None


class ManualCourierProvider:
    """Local sandbox provider with the contract of a real courier API."""

    name = "manual"

    def create_shipment(self, order):
        return ShipmentResult(
            provider=self.name,
            provider_reference=f"manual-order-{order.pk}",
            tracking_number=f"DEMO-{order.pk:06d}",
            payload={"mode": "sandbox", "order_id": order.pk},
        )


def get_courier_provider():
    provider_name = getattr(settings, "FULFILLMENT_PROVIDER", "manual")
    if provider_name == "manual":
        return ManualCourierProvider()
    raise RuntimeError(f"Unsupported fulfillment provider: {provider_name}")


def mark_order_ready_for_fulfillment(order):
    """Set the next fulfillment state after inventory is safely handled."""

    if order.inventory_status == Order.INVENTORY_NOT_REQUIRED:
        status = Order.FULFILLMENT_NOT_REQUIRED
    elif order.inventory_status == Order.INVENTORY_DEDUCTED:
        status = Order.FULFILLMENT_READY
    else:
        return
    if order.fulfillment_status != status:
        order.fulfillment_status = status
        order.save(update_fields=["fulfillment_status", "updated_at"])


def create_shipment_for_order(order):
    """Create one shipment after payment and inventory are confirmed."""

    with transaction.atomic():
        locked_order = (
            Order.objects.select_for_update()
            .prefetch_related("items")
            .get(pk=order.pk)
        )
        if locked_order.payment_status != Order.PAYMENT_PAID:
            raise ValueError("Only paid orders can be shipped.")
        if locked_order.inventory_status == Order.INVENTORY_UNAVAILABLE:
            raise ValueError("This order cannot ship because stock is unavailable.")
        if locked_order.fulfillment_status == Order.FULFILLMENT_NOT_REQUIRED:
            raise ValueError("This digital-only order does not need shipping.")
        if hasattr(locked_order, "shipment"):
            return locked_order.shipment
        if locked_order.inventory_status != Order.INVENTORY_DEDUCTED:
            raise ValueError("Inventory must be deducted before shipping.")
        if not all(
            [
                locked_order.shipping_address,
                locked_order.shipping_city,
                locked_order.shipping_country,
            ]
        ):
            raise ValueError("A complete shipping address is required.")

        result = get_courier_provider().create_shipment(locked_order)
        shipment = Shipment.objects.create(
            order=locked_order,
            provider=result.provider,
            provider_reference=result.provider_reference,
            tracking_number=result.tracking_number,
            tracking_url=result.tracking_url,
            provider_payload=result.payload or {},
        )
        locked_order.fulfillment_status = Order.FULFILLMENT_SHIPMENT_CREATED
        locked_order.save(update_fields=["fulfillment_status", "updated_at"])
        return shipment


def update_shipment_status(shipment, status):
    """Apply a courier callback/status poll idempotently to local state."""

    if status not in dict(Shipment.STATUS_CHOICES):
        raise ValueError(f"Unsupported shipment status: {status}")
    with transaction.atomic():
        shipment = (
            Shipment.objects.select_for_update()
            .select_related("order")
            .get(pk=shipment.pk)
        )
        shipment.status = status
        update_fields = ["status", "updated_at"]
        if (
            status in {Shipment.IN_TRANSIT, Shipment.OUT_FOR_DELIVERY}
            and not shipment.shipped_at
        ):
            shipment.shipped_at = timezone.now()
            update_fields.append("shipped_at")
        if status == Shipment.DELIVERED and not shipment.delivered_at:
            shipment.delivered_at = timezone.now()
            update_fields.append("delivered_at")
        shipment.save(update_fields=update_fields)
        order_status = {
            Shipment.CREATED: Order.FULFILLMENT_SHIPMENT_CREATED,
            Shipment.IN_TRANSIT: Order.FULFILLMENT_IN_TRANSIT,
            Shipment.OUT_FOR_DELIVERY: Order.FULFILLMENT_OUT_FOR_DELIVERY,
            Shipment.DELIVERED: Order.FULFILLMENT_DELIVERED,
            Shipment.EXCEPTION: Order.FULFILLMENT_EXCEPTION,
        }[status]
        if shipment.order.fulfillment_status != order_status:
            shipment.order.fulfillment_status = order_status
            shipment.order.save(update_fields=["fulfillment_status", "updated_at"])
        return shipment
