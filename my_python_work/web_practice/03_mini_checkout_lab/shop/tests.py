from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.active_product = Product.objects.create(
            name="Canvas Tote",
            slug="canvas-tote",
            description="A reusable everyday bag.",
            price=Decimal("12.50"),
            stock=4,
        )
        Product.objects.create(
            name="Hidden Sample",
            slug="hidden-sample",
            description="Not shown to customers.",
            price=Decimal("9.99"),
            stock=2,
            is_active=False,
        )

    def test_product_list_shows_active_products_only(self):
        response = self.client.get(reverse("shop:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Canvas Tote")
        self.assertNotContains(response, "Hidden Sample")

    def test_product_detail_shows_product_information(self):
        response = self.client.get(
            reverse("shop:product_detail", kwargs={"slug": self.active_product.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Canvas Tote")
        self.assertContains(response, "$12.50")

    def test_inactive_product_detail_returns_not_found(self):
        response = self.client.get(
            reverse("shop:product_detail", kwargs={"slug": "hidden-sample"})
        )

        self.assertEqual(response.status_code, 404)
