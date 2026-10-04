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
        self.inactive_product = Product.objects.create(
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

    def test_add_to_cart_stores_quantity_in_session(self):
        response = self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )

        self.assertRedirects(
            response,
            reverse(
                "shop:product_detail",
                kwargs={"slug": self.active_product.slug},
            ),
        )
        self.assertEqual(
            self.client.session["cart"],
            {str(self.active_product.pk): 1},
        )

    def test_cart_update_is_limited_by_current_stock(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )
        response = self.client.post(
            reverse("shop:update_cart", kwargs={"product_id": self.active_product.pk}),
            {"quantity": "99"},
        )

        self.assertRedirects(response, reverse("shop:cart_detail"))
        self.assertEqual(
            self.client.session["cart"],
            {str(self.active_product.pk): self.active_product.stock},
        )

    def test_inactive_product_cannot_be_added_to_cart(self):
        response = self.client.post(
            reverse(
                "shop:add_to_cart",
                kwargs={"product_id": self.inactive_product.pk},
            ),
        )

        self.assertEqual(response.status_code, 404)
        self.assertNotIn("cart", self.client.session)

    def test_cart_page_shows_line_total(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )

        response = self.client.get(reverse("shop:cart_detail"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "$12.50")

    def test_remove_from_cart_clears_the_product(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )
        response = self.client.post(
            reverse(
                "shop:remove_from_cart",
                kwargs={"product_id": self.active_product.pk},
            ),
        )

        self.assertRedirects(response, reverse("shop:cart_detail"))
        self.assertEqual(self.client.session["cart"], {})
