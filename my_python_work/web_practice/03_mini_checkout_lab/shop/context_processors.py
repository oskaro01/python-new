"""Template context shared by the shop pages."""

from .cart import get_cart_count


def cart_summary(request):
    return {"cart_count": get_cart_count(request)}
