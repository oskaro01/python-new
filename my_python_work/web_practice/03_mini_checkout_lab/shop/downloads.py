"""Signed, expiring access to paid digital order items."""

from urllib.parse import urlencode

from django.conf import settings
from django.core import signing
from django.urls import reverse


DOWNLOAD_TOKEN_SALT = "shop.digital-download"


def create_download_token(item):
    return signing.dumps(
        {"order_id": item.order_id, "item_id": item.pk},
        salt=DOWNLOAD_TOKEN_SALT,
        compress=True,
    )


def read_download_token(token):
    return signing.loads(
        token,
        salt=DOWNLOAD_TOKEN_SALT,
        max_age=settings.DIGITAL_DOWNLOAD_MAX_AGE,
    )


def build_download_url(request, item):
    path = reverse(
        "shop:download_order_item",
        kwargs={"order_id": item.order_id, "item_id": item.pk},
    )
    return request.build_absolute_uri(
        f"{path}?{urlencode({'token': create_download_token(item)})}"
    )
