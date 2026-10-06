"""Shipping methods and server-owned rates for the checkout lab."""

from decimal import Decimal


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
