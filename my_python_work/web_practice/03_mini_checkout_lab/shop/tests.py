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

    def test_checkout_redirects_when_cart_is_empty(self):
        response = self.client.get(reverse("shop:checkout"))

        self.assertRedirects(response, reverse("shop:cart_detail"))

    def test_checkout_shows_customer_form_with_cart(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )

        response = self.client.get(reverse("shop:checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Customer details")
        self.assertContains(response, "$12.50")

    def test_invalid_checkout_data_returns_form_errors(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )

        response = self.client.post(
            reverse("shop:checkout_review"),
            {"full_name": "", "email": "not-an-email"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "This field is required.", status_code=400)
        self.assertContains(
            response,
            "Enter a valid email address.",
            status_code=400,
        )

    def test_valid_checkout_shows_review_without_creating_order(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )

        response = self.client.post(
            reverse("shop:checkout_review"),
            {
                "full_name": "Ayzal Yohan",
                "email": "ayzal@example.com",
                "phone": "01700000000",
                "notes": "Please leave at the front desk.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ayzal Yohan")
        self.assertContains(response, "ayzal@example.com")
        self.assertContains(response, "Review complete")
        self.assertContains(response, "$12.50")
