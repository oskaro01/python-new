"""Public product catalog views."""

import logging
from pathlib import Path

from django.contrib import messages
from django.core import signing
from django.core.files.storage import default_storage
from django.db import transaction
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
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
from .downloads import build_download_url, read_download_token
from .inventory import deduct_paid_order_inventory
from .models import Order, OrderItem, Product
from .payments import (
    PaymentConfigurationError,
    construct_stripe_event,
    create_stripe_checkout_session,
    stripe_is_configured,
)
from .shipping import mark_order_ready_for_fulfillment, shipping_cost


CHECKOUT_SESSION_KEY = "checkout_customer"
LAST_ORDER_SESSION_KEY = "last_order_id"
logger = logging.getLogger(__name__)


def confirm_stripe_payment(session):
    order_id = (session.get("metadata") or {}).get("order_id")
    if not order_id or session.get("payment_status") != "paid":
        return

    with transaction.atomic():
        order = Order.objects.select_for_update().filter(pk=order_id).first()
        if not order or order.payment_status == Order.PAYMENT_PAID:
            return

        order.payment_status = Order.PAYMENT_PAID
        order.status = Order.PROCESSING
        order.payment_provider = "stripe"
        order.payment_reference = session.get("payment_intent") or session.get(
            "id", ""
        )
        order.payment_method = "card"
        order.paid_at = timezone.now()
        order.save(
            update_fields=[
                "payment_status",
                "status",
                "payment_provider",
                "payment_reference",
                "payment_method",
                "paid_at",
                "updated_at",
            ]
        )
        deduct_paid_order_inventory(order)
        mark_order_ready_for_fulfillment(order)
        try:
            send_order_receipt(order)
        except Exception:
            logger.exception("Receipt email failed for order %s", order.pk)
        else:
            order.receipt_sent_at = timezone.now()
            order.save(update_fields=["receipt_sent_at", "updated_at"])


def fail_stripe_payment(session):
    order_id = (session.get("metadata") or {}).get("order_id")
    if not order_id:
        return

    with transaction.atomic():
        order = Order.objects.select_for_update().filter(pk=order_id).first()
        if not order or order.payment_status != Order.PAYMENT_PENDING:
            return

        order.payment_status = Order.PAYMENT_FAILED
        order.payment_provider = "stripe"
        order.payment_reference = session.get("payment_intent") or session.get(
            "id", ""
        )
        order.save(
            update_fields=[
                "payment_status",
                "payment_provider",
                "payment_reference",
                "updated_at",
            ]
        )


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

    shipping_amount = (
        shipping_cost(form.cleaned_data["shipping_method"])
        if form.cleaned_data["shipping_method"]
        else 0
    )

    return render(
        request,
        "shop/checkout_review.html",
        {
            "title": "Checkout Review",
            "customer": form.cleaned_data,
            "items": items,
            "cart_total": get_cart_total(items),
            "shipping_amount": shipping_amount,
            "order_total": get_cart_total(items) + shipping_amount,
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
    shipping_amount = (
        shipping_cost(form.cleaned_data["shipping_method"])
        if cart_requires_shipping(items)
        else 0
    )
    with transaction.atomic():
        order = Order.objects.create(
            full_name=form.cleaned_data["full_name"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"],
            shipping_address=form.cleaned_data["shipping_address"],
            shipping_city=form.cleaned_data["shipping_city"],
            shipping_postal_code=form.cleaned_data["shipping_postal_code"],
            shipping_country=form.cleaned_data["shipping_country"],
            shipping_method=form.cleaned_data["shipping_method"],
            shipping_amount=shipping_amount,
            notes=form.cleaned_data["notes"],
            total_amount=cart_total + shipping_amount,
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
                    digital_file_name=item["product"].digital_file.name,
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
    download_items = []
    if order.payment_status == Order.PAYMENT_PAID:
        for item in order.items.all():
            if (
                item.product_type in {Product.DIGITAL, Product.HYBRID}
                and item.digital_file_name
            ):
                item.download_url = build_download_url(request, item)
                download_items.append(item)
    return render(
        request,
        "shop/order_success.html",
        {
            "title": "Order placed",
            "order": order,
            "download_items": download_items,
            "stripe_payment_enabled": stripe_is_configured(),
        },
    )


@require_GET
def download_order_item(request, order_id, item_id):
    token = request.GET.get("token", "")
    try:
        token_data = read_download_token(token)
    except (signing.BadSignature, signing.SignatureExpired):
        raise Http404 from None
    if token_data != {"order_id": order_id, "item_id": item_id}:
        raise Http404

    item = get_object_or_404(
        OrderItem.objects.select_related("order"),
        pk=item_id,
        order_id=order_id,
        product_type__in=[Product.DIGITAL, Product.HYBRID],
    )
    if item.order.payment_status != Order.PAYMENT_PAID or not item.digital_file_name:
        raise Http404
    try:
        file_handle = default_storage.open(item.digital_file_name, "rb")
    except FileNotFoundError:
        raise Http404 from None
    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=Path(item.digital_file_name).name,
    )


@require_POST
def start_payment(request, order_id):
    if request.session.get(LAST_ORDER_SESSION_KEY) != order_id:
        raise Http404

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
    )
    if order.payment_status != Order.PAYMENT_PENDING:
        return redirect("shop:order_success", order_id=order.pk)

    try:
        session = create_stripe_checkout_session(order, request)
    except PaymentConfigurationError as error:
        messages.error(request, str(error))
        return redirect("shop:order_success", order_id=order.pk)

    order.payment_provider = "stripe"
    order.payment_reference = session.id
    order.payment_method = "card"
    order.save(
        update_fields=[
            "payment_provider",
            "payment_reference",
            "payment_method",
            "updated_at",
        ]
    )
    return redirect(session.url)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    try:
        event = construct_stripe_event(
            request.body,
            request.headers.get("Stripe-Signature", ""),
        )
    except (PaymentConfigurationError, ValueError, TypeError):
        return HttpResponse("Invalid webhook", status=400)

    session = event["data"]["object"]
    if event["type"] in {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }:
        confirm_stripe_payment(session)
    elif event["type"] == "checkout.session.async_payment_failed":
        fail_stripe_payment(session)

    return JsonResponse({"received": True})


@require_POST
def simulate_payment(request, order_id):
    if request.session.get(LAST_ORDER_SESSION_KEY) != order_id:
        raise Http404

    order = get_object_or_404(Order, pk=order_id)
    if order.payment_status == Order.PAYMENT_PENDING:
        order.payment_status = Order.PAYMENT_PAID
        order.status = Order.PROCESSING
        order.payment_provider = "demo"
        order.payment_reference = f"demo-order-{order.pk}"
        order.payment_method = "demo"
        order.paid_at = timezone.now()
        order.save(
            update_fields=[
                "payment_status",
                "status",
                "payment_provider",
                "payment_reference",
                "payment_method",
                "paid_at",
                "updated_at",
            ]
        )
        deduct_paid_order_inventory(order)
        mark_order_ready_for_fulfillment(order)
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
