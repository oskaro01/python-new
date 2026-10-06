"""Payment-provider boundary for the checkout lab."""

from decimal import Decimal

from django.conf import settings
from django.urls import reverse


class PaymentConfigurationError(RuntimeError):
    """Raised when a real payment provider is not configured."""


def stripe_is_configured():
    return settings.PAYMENT_PROVIDER == "stripe" and bool(
        settings.STRIPE_SECRET_KEY
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
