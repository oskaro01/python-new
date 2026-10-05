"""Email helpers for shop order messages."""

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_order_receipt(order):
    body = render_to_string(
        "shop/emails/order_receipt.txt",
        {"order": order},
    )
    email = EmailMessage(
        subject=f"Receipt for Order #{order.pk}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    return email.send(fail_silently=False)
