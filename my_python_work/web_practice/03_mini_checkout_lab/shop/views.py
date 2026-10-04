"""Public product catalog views."""

from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

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
