"""Public product catalog views."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .cart import (
    add_product,
    get_cart_items,
    get_cart_total,
    remove_product,
    update_product,
)
from .forms import CheckoutForm
from .models import Product


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
            "form": CheckoutForm(),
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

    form = CheckoutForm(request.POST)
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
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if product.stock <= 0:
        messages.error(request, f"{product.name} is out of stock.")
    else:
        add_product(request, product)
        messages.success(request, f"{product.name} was added to your cart.")

    return redirect("shop:product_detail", slug=product.slug)


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
        if quantity > product.stock:
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
