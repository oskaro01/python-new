"""Session-cart helpers for the ecommerce learning lab."""

from decimal import Decimal

from .models import Product


CART_SESSION_KEY = "cart"
MAX_DIGITAL_QUANTITY = 99


def get_cart_data(request):
    raw_cart = request.session.get(CART_SESSION_KEY, {})
    if not isinstance(raw_cart, dict):
        return {}

    cart = {}
    for product_id, quantity in raw_cart.items():
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        if quantity > 0:
            cart[str(product_id)] = quantity

    return cart


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def add_product(request, product, quantity=1):
    cart = get_cart_data(request)
    product_id = str(product.pk)
    current_quantity = cart.get(product_id, 0)
    maximum = product.stock if product.inventory_tracked else MAX_DIGITAL_QUANTITY
    cart[product_id] = min(current_quantity + quantity, maximum)
    save_cart(request, cart)


def update_product(request, product, quantity):
    cart = get_cart_data(request)
    product_id = str(product.pk)

    if quantity <= 0 or (product.inventory_tracked and product.stock <= 0):
        cart.pop(product_id, None)
    else:
        maximum = product.stock if product.inventory_tracked else MAX_DIGITAL_QUANTITY
        cart[product_id] = min(quantity, maximum)

    save_cart(request, cart)


def remove_product(request, product_id):
    cart = get_cart_data(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)


def get_cart_count(request):
    return sum(get_cart_data(request).values())


def get_cart_total(items):
    return sum(
        (item["line_total"] for item in items),
        Decimal("0.00"),
    )


def get_cart_items(request):
    cart = get_cart_data(request)
    if not cart:
        return []

    products = Product.objects.filter(
        pk__in=cart.keys(),
        is_active=True,
    )
    products_by_id = {str(product.pk): product for product in products}
    cleaned_cart = {}
    items = []

    for product_id, requested_quantity in cart.items():
        product = products_by_id.get(product_id)
        if product is None or (product.inventory_tracked and product.stock <= 0):
            continue

        maximum = product.stock if product.inventory_tracked else MAX_DIGITAL_QUANTITY
        quantity = min(requested_quantity, maximum)
        cleaned_cart[product_id] = quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "line_total": product.price * quantity,
                "max_quantity": maximum,
            }
        )

    if cleaned_cart != cart:
        save_cart(request, cleaned_cart)

    return items


def cart_requires_shipping(items):
    return any(item["product"].requires_shipping for item in items)
