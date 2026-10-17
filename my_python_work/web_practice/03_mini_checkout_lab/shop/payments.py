"""Payment-provider boundary for the checkout lab."""

from decimal import Decimal
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.urls import reverse


class PaymentConfigurationError(RuntimeError):
    """Raised when a real payment provider is not configured."""


class BkashAPIError(RuntimeError):
    """Raised when bKash rejects or cannot answer an API request."""


def stripe_is_configured():
    return settings.PAYMENT_PROVIDER == "stripe" and bool(
        settings.STRIPE_SECRET_KEY
    )


def bkash_is_configured():
    return settings.PAYMENT_PROVIDER == "bkash" and all(
        [
            settings.BKASH_BASE_URL,
            settings.BKASH_APP_KEY,
            settings.BKASH_APP_SECRET,
            settings.BKASH_USERNAME,
            settings.BKASH_PASSWORD,
        ]
    )


_bkash_token = ""
_bkash_token_expires_at = 0.0


def _bkash_request(method, path, payload=None, token="", extra_headers=None):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-App-Key"] = settings.BKASH_APP_KEY
    if extra_headers:
        headers.update(extra_headers)
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        f"{settings.BKASH_BASE_URL}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=settings.BKASH_TIMEOUT) as response:
            return json.loads(response.read().decode())
    except (HTTPError, URLError, ValueError) as error:
        raise BkashAPIError("bKash API request failed.") from error


def _bkash_access_token():
    global _bkash_token, _bkash_token_expires_at
    now = time.monotonic()
    if _bkash_token and now < _bkash_token_expires_at:
        return _bkash_token
    response = _bkash_request(
        "POST",
        "/auth/grant-token",
        {
            "app_key": settings.BKASH_APP_KEY,
            "app_secret": settings.BKASH_APP_SECRET,
        },
        extra_headers={
            "username": settings.BKASH_USERNAME,
            "password": settings.BKASH_PASSWORD,
        },
    )
    token = response.get("id_token") or response.get("access_token")
    if not token:
        raise BkashAPIError("bKash did not return an access token.")
    expires_in = int(response.get("expires_in") or 3600)
    _bkash_token = token
    _bkash_token_expires_at = now + max(expires_in - 60, 60)
    return _bkash_token


def create_bkash_payment(order, callback_url):
    if not bkash_is_configured():
        raise PaymentConfigurationError(
            "Configure PAYMENT_PROVIDER=bkash and the BKASH_* credentials first."
        )
    return _bkash_request(
        "POST",
        "/payment/create",
        {
            "callbackURL": callback_url,
            "payerReference": str(order.customer_id or order.email)[:255],
            "amount": f"{order.total_amount:.2f}",
            "currency": settings.BKASH_CURRENCY,
            "intent": "sale",
            "merchantInvoiceNumber": f"order-{order.pk}",
        },
        token=_bkash_access_token(),
    )


def execute_bkash_payment(payment_id):
    if not bkash_is_configured():
        raise PaymentConfigurationError(
            "Configure PAYMENT_PROVIDER=bkash and the BKASH_* credentials first."
        )
    return _bkash_request(
        "POST",
        "/payment/execute",
        {"paymentId": payment_id},
        token=_bkash_access_token(),
    )


def create_stripe_checkout_session(order, request):
    if not stripe_is_configured():
        raise PaymentConfigurationError(
            "Configure PAYMENT_PROVIDER=stripe and STRIPE_SECRET_KEY first."
        )

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    line_items = [
        {
            "price_data": {
                "currency": settings.PAYMENT_CURRENCY,
                "product_data": {"name": item.product_name},
                "unit_amount": int(item.unit_price * Decimal("100")),
            },
            "quantity": item.quantity,
        }
        for item in order.items.all()
    ]
    if order.shipping_amount:
        line_items.append(
            {
                "price_data": {
                    "currency": settings.PAYMENT_CURRENCY,
                    "product_data": {"name": "Shipping"},
                    "unit_amount": int(order.shipping_amount * Decimal("100")),
                },
                "quantity": 1,
            }
        )

    return stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        customer_email=order.email,
        client_reference_id=str(order.pk),
        metadata={"order_id": str(order.pk)},
        success_url=request.build_absolute_uri(
            reverse("shop:order_success", kwargs={"order_id": order.pk})
        ),
        cancel_url=request.build_absolute_uri(
            reverse("shop:order_success", kwargs={"order_id": order.pk})
        ),
    )


def construct_stripe_event(payload, signature):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise PaymentConfigurationError("STRIPE_WEBHOOK_SECRET is not configured.")

    import stripe

    return stripe.Webhook.construct_event(
        payload,
        signature,
        settings.STRIPE_WEBHOOK_SECRET,
    )


def refund_payment(order):
    """Refund one paid order and return the provider refund reference."""

    if order.payment_status == order.PAYMENT_REFUNDED:
        return order.refund_reference
    if order.payment_status != order.PAYMENT_PAID:
        raise PaymentConfigurationError("Only paid orders can be refunded.")

    if order.payment_provider == "demo":
        return f"demo-refund-order-{order.pk}"
    if order.payment_provider != "stripe" or not stripe_is_configured():
        raise PaymentConfigurationError("This order has no refundable payment provider.")

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    refund = stripe.Refund.create(
        payment_intent=order.payment_reference,
        idempotency_key=f"order-{order.pk}-refund",
    )
    return refund.id
