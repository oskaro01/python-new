"""Shipping rates and the courier-provider boundary for fulfillment."""

from dataclasses import dataclass
from decimal import Decimal
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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


class PathaoCourierProvider:
    """Pathao Merchant API adapter; disabled unless explicitly selected."""

    name = "pathao"

    def __init__(self):
        self.base_url = getattr(settings, "PATHAO_BASE_URL", "").rstrip("/")
        self.client_id = getattr(settings, "PATHAO_CLIENT_ID", "")
        self.client_secret = getattr(settings, "PATHAO_CLIENT_SECRET", "")
        self.username = getattr(settings, "PATHAO_USERNAME", "")
        self.password = getattr(settings, "PATHAO_PASSWORD", "")
        self.store_id = getattr(settings, "PATHAO_STORE_ID", "")
        self.timeout = getattr(settings, "PATHAO_TIMEOUT", 20)
        if not all(
            [
                self.base_url,
                self.client_id,
                self.client_secret,
                self.username,
                self.password,
                self.store_id,
            ]
        ):
            raise RuntimeError("Pathao API credentials and store ID are required.")

    def _request(self, method, path, payload=None, token=""):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        body = json.dumps(payload).encode() if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode())
        except (HTTPError, URLError, ValueError) as error:
            raise RuntimeError("Pathao API request failed.") from error

    def _access_token(self):
        response = self._request(
            "POST",
            "/aladdin/api/v1/issue-token",
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password,
                "grant_type": "password",
            },
        )
        token = response.get("access_token")
        if not token:
            raise RuntimeError("Pathao did not return an access token.")
        return token

    def create_shipment(self, order):
        item_count = sum(item.quantity for item in order.items.all())
        weight = sum(
            (item.product.weight_grams if item.product else 0) * item.quantity
            for item in order.items.all()
        ) / 1000 or 0.5
        payload = {
            "store_id": int(self.store_id),
            "merchant_order_id": str(order.pk),
            "sender_name": getattr(settings, "PATHAO_SENDER_NAME", ""),
            "sender_phone": getattr(settings, "PATHAO_SENDER_PHONE", ""),
            "recipient_name": order.full_name,
            "recipient_phone": order.phone,
            "recipient_address": order.shipping_address,
            "recipient_city": int(getattr(settings, "PATHAO_RECIPIENT_CITY_ID", 0)),
            "recipient_zone": int(getattr(settings, "PATHAO_RECIPIENT_ZONE_ID", 0)),
            "recipient_area": int(getattr(settings, "PATHAO_RECIPIENT_AREA_ID", 0)),
            "delivery_type": int(getattr(settings, "PATHAO_DELIVERY_TYPE", 48)),
            "item_type": int(getattr(settings, "PATHAO_ITEM_TYPE", 2)),
            "item_quantity": item_count,
            "item_weight": weight,
            "amount_to_collect": 0,
            "item_description": ", ".join(
                item.product_name for item in order.items.all()
            ),
        }
        if not payload["sender_name"] or not payload["sender_phone"]:
            raise RuntimeError("Pathao sender details are required.")
        if not all(
            [
                payload["recipient_city"],
                payload["recipient_zone"],
                payload["recipient_area"],
            ]
        ):
            raise RuntimeError("Pathao recipient city, zone, and area IDs are required.")
        response = self._request(
            "POST",
            "/aladdin/api/v1/orders",
            payload,
            token=self._access_token(),
        )
        data = response.get("data") or {}
        tracking_number = data.get("consignment_id") or data.get("tracking_code")
        if not tracking_number:
            raise RuntimeError("Pathao did not return a tracking reference.")
        return ShipmentResult(
            provider=self.name,
            provider_reference=str(data.get("consignment_id", tracking_number)),
            tracking_number=str(tracking_number),
            payload=response,
        )


def get_courier_provider():
    provider_name = getattr(settings, "FULFILLMENT_PROVIDER", "manual")
    if provider_name == "manual":
        return ManualCourierProvider()
    if provider_name == "pathao":
        return PathaoCourierProvider()
    raise RuntimeError(f"Unsupported fulfillment provider: {provider_name}")


def mark_order_ready_for_fulfillment(order):
    """Set the next fulfillment state after inventory is safely handled."""

    if order.inventory_status == Order.INVENTORY_NOT_REQUIRED:
        status = Order.FULFILLMENT_NOT_REQUIRED
        order_status = Order.COMPLETED
    elif order.inventory_status == Order.INVENTORY_DEDUCTED:
        status = Order.FULFILLMENT_READY
        order_status = Order.PROCESSING
    else:
        return
    update_fields = []
    if order.fulfillment_status != status:
        order.fulfillment_status = status
        update_fields.append("fulfillment_status")
    if order.status != order_status:
        order.status = order_status
        update_fields.append("status")
    if update_fields:
        order.save(update_fields=[*update_fields, "updated_at"])


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
        desired_order_status = (
            Order.COMPLETED
            if status == Shipment.DELIVERED
            else Order.PROCESSING
        )
        if (
            shipment.order.fulfillment_status != order_status
            or shipment.order.status != desired_order_status
        ):
            shipment.order.fulfillment_status = order_status
            update_fields = ["fulfillment_status", "updated_at"]
            if status == Shipment.DELIVERED:
                shipment.order.status = Order.COMPLETED
                update_fields.append("status")
            elif status in {
                Shipment.CREATED,
                Shipment.IN_TRANSIT,
                Shipment.OUT_FOR_DELIVERY,
                Shipment.EXCEPTION,
            }:
                shipment.order.status = Order.PROCESSING
                update_fields.append("status")
            shipment.order.save(update_fields=update_fields)
        return shipment
