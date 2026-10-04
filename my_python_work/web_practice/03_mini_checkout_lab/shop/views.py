"""Public product catalog views."""

from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .cart import add_product, get_cart_items, remove_product, update_product
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
    cart_total = sum(
        (item["line_total"] for item in items),
        Decimal("0.00"),
    )
    return render(
        request,
        "shop/cart_detail.html",
        {
            "title": "Your Cart",
            "items": items,
            "cart_total": cart_total,
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
