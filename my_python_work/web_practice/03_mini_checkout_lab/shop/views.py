"""Public product catalog views."""

import logging

from django.contrib import messages
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .cart import (
    add_product,
    CART_SESSION_KEY,
    get_cart_items,
    get_cart_count,
    get_cart_total,
    cart_requires_shipping,
    remove_product,
    update_product,
)
from .forms import CheckoutForm
from .emails import send_order_receipt
from .models import Order, OrderItem, Product


CHECKOUT_SESSION_KEY = "checkout_customer"
LAST_ORDER_SESSION_KEY = "last_order_id"
logger = logging.getLogger(__name__)


@require_GET
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(
        request,
        "shop/product_list.html",
        {
            "title": "Product Catalog",
            "products": products,
        },
    )


@require_GET
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(
        request,
        "shop/product_detail.html",
        {
            "title": product.name,
            "product": product,
        },
    )


@require_GET
def cart_detail(request):
    items = get_cart_items(request)
    cart_total = get_cart_total(items)
    return render(
        request,
        "shop/cart_detail.html",
        {
            "title": "Your Cart",
            "items": items,
            "cart_total": cart_total,
        },
    )


@require_GET
def checkout(request):
    items = get_cart_items(request)
    if not items:
        messages.info(request, "Add a product before starting checkout.")
        return redirect("shop:cart_detail")

    return render(
        request,
        "shop/checkout.html",
        {
            "title": "Checkout",
            "form": CheckoutForm(requires_shipping=cart_requires_shipping(items)),
            "items": items,
            "cart_total": get_cart_total(items),
        },
    )


@require_POST
def checkout_review(request):
    items = get_cart_items(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("shop:cart_detail")

    form = CheckoutForm(
        request.POST,
        requires_shipping=cart_requires_shipping(items),
    )
    if not form.is_valid():
        return render(
            request,
            "shop/checkout.html",
            {
                "title": "Checkout",
                "form": form,
                "items": items,
                "cart_total": get_cart_total(items),
            },
            status=400,
        )

    request.session[CHECKOUT_SESSION_KEY] = form.cleaned_data
    request.session.modified = True

    # Reload the cart before displaying the review so totals come from current
    # database prices and stock, never from browser-submitted values.
    items = get_cart_items(request)
    if not items:
        messages.info(request, "Your cart is no longer available.")
        return redirect("shop:cart_detail")

    return render(
        request,
        "shop/checkout_review.html",
        {
            "title": "Checkout Review",
            "customer": form.cleaned_data,
            "items": items,
            "cart_total": get_cart_total(items),
        },
    )


@require_POST
def place_order(request):
    items = get_cart_items(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("shop:cart_detail")

    checkout_data = request.session.get(CHECKOUT_SESSION_KEY, {})
    form = CheckoutForm(
        checkout_data,
        requires_shipping=cart_requires_shipping(items),
    )
    if not form.is_valid():
        messages.info(request, "Please enter your checkout details again.")
        return redirect("shop:checkout")

    cart_total = get_cart_total(items)
    with transaction.atomic():
        order = Order.objects.create(
            full_name=form.cleaned_data["full_name"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"],
            shipping_address=form.cleaned_data["shipping_address"],
            shipping_city=form.cleaned_data["shipping_city"],
            shipping_postal_code=form.cleaned_data["shipping_postal_code"],
            shipping_country=form.cleaned_data["shipping_country"],
            notes=form.cleaned_data["notes"],
            total_amount=cart_total,
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=item["product"],
                    product_name=item["product"].name,
                    product_type=item["product"].product_type,
                    unit_price=item["product"].price,
                    quantity=item["quantity"],
                    line_total=item["line_total"],
                )
                for item in items
            ]
        )

    request.session.pop(CART_SESSION_KEY, None)
    request.session.pop(CHECKOUT_SESSION_KEY, None)
    request.session[LAST_ORDER_SESSION_KEY] = order.pk
    request.session.modified = True
    return redirect("shop:order_success", order_id=order.pk)


@require_GET
def order_success(request, order_id):
    if request.session.get(LAST_ORDER_SESSION_KEY) != order_id:
        raise Http404

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
    )
    return render(
        request,
        "shop/order_success.html",
        {
            "title": "Order placed",
            "order": order,
        },
    )


@require_POST
def simulate_payment(request, order_id):
    if request.session.get(LAST_ORDER_SESSION_KEY) != order_id:
        raise Http404

    order = get_object_or_404(Order, pk=order_id)
    if order.payment_status == Order.PAYMENT_PENDING:
        order.payment_status = Order.PAYMENT_PAID
        order.save(update_fields=["payment_status", "updated_at"])
        try:
            send_order_receipt(order)
        except Exception:
            logger.exception("Receipt email failed for order %s", order.pk)
            messages.error(
                request,
                "Demo payment was recorded, but the receipt could not be sent.",
            )
        else:
            order.receipt_sent_at = timezone.now()
            order.save(update_fields=["receipt_sent_at", "updated_at"])
            messages.success(request, "Demo payment marked as paid. Receipt sent.")
    else:
        messages.info(request, "This order already has a payment result.")

    return redirect("shop:order_success", order_id=order.pk)


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wants_json = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if not product.is_available:
        message = f"{product.name} is out of stock."
        if wants_json:
            return JsonResponse(
                {"ok": False, "message": message, "cart_count": get_cart_count(request)},
                status=400,
            )
        messages.error(request, message)
    else:
        add_product(request, product)
        message = f"{product.name} was added to your cart."
        if wants_json:
            return JsonResponse(
                {"ok": True, "message": message, "cart_count": get_cart_count(request)},
            )
        messages.success(request, message)

    if request.POST.get("return_to") == "detail":
        return redirect("shop:product_detail", slug=product.slug)
    return redirect("shop:product_list")


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    raw_quantity = request.POST.get("quantity", "").strip()

    try:
        quantity = int(raw_quantity)
    except ValueError:
        messages.error(request, "Quantity must be a whole number.")
    else:
        update_product(request, product, quantity)
        if product.inventory_tracked and quantity > product.stock:
            messages.info(
                request,
                f"{product.name} was limited to the {product.stock} available.",
            )
        elif quantity <= 0:
            messages.success(request, f"{product.name} was removed from your cart.")
        else:
            messages.success(request, "Cart updated.")

    return redirect("shop:cart_detail")


@require_POST
def remove_from_cart(request, product_id):
    remove_product(request, product_id)
    messages.success(request, "Item removed from your cart.")
    return redirect("shop:cart_detail")
