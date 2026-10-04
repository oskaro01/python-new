from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Order, OrderItem, Product


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
            reverse("shop:product_list"),
        )
        self.assertEqual(
            self.client.session["cart"],
            {str(self.active_product.pk): 1},
        )

    def test_ajax_add_to_cart_returns_json_without_redirecting(self):
        response = self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "ok": True,
                "message": "Canvas Tote was added to your cart.",
                "cart_count": 1,
            },
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
                "shipping_address": "12 River Road",
                "shipping_city": "Dhaka",
                "shipping_postal_code": "1205",
                "shipping_country": "Bangladesh",
                "notes": "Please leave at the front desk.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ayzal Yohan")
        self.assertContains(response, "ayzal@example.com")
        self.assertContains(response, "pending order")
        self.assertContains(response, "Place order")
        self.assertContains(response, "$12.50")
        self.assertEqual(Order.objects.count(), 0)

    def test_place_order_creates_order_items_and_clears_cart(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )
        self.client.post(
            reverse("shop:checkout_review"),
            {
                "full_name": "Ayzal Yohan",
                "email": "ayzal@example.com",
                "phone": "",
                "shipping_address": "12 River Road",
                "shipping_city": "Dhaka",
                "shipping_postal_code": "1205",
                "shipping_country": "Bangladesh",
                "notes": "",
            },
        )

        response = self.client.post(reverse("shop:place_order"))

        order = Order.objects.get()
        item = OrderItem.objects.get(order=order)
        self.assertRedirects(
            response,
            reverse("shop:order_success", kwargs={"order_id": order.pk}),
        )
        self.assertEqual(order.status, Order.PENDING)
        self.assertEqual(order.payment_status, Order.PAYMENT_PENDING)
        self.assertEqual(order.total_amount, Decimal("12.50"))
        self.assertEqual(order.shipping_address, "12 River Road")
        self.assertEqual(order.shipping_city, "Dhaka")
        self.assertEqual(order.shipping_postal_code, "1205")
        self.assertEqual(order.shipping_country, "Bangladesh")
        self.assertEqual(item.product_name, "Canvas Tote")
        self.assertEqual(item.unit_price, Decimal("12.50"))
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.line_total, Decimal("12.50"))
        self.assertNotIn("cart", self.client.session)
        self.assertNotIn("checkout_customer", self.client.session)

    def test_simulate_payment_marks_current_order_paid(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )
        self.client.post(
            reverse("shop:checkout_review"),
            {
                "full_name": "Ayzal Yohan",
                "email": "ayzal@example.com",
                "phone": "",
                "shipping_address": "12 River Road",
                "shipping_city": "Dhaka",
                "shipping_postal_code": "1205",
                "shipping_country": "Bangladesh",
                "notes": "",
            },
        )
        self.client.post(reverse("shop:place_order"))
        order = Order.objects.get()

        response = self.client.post(
            reverse("shop:simulate_payment", kwargs={"order_id": order.pk}),
        )

        self.assertRedirects(
            response,
            reverse("shop:order_success", kwargs={"order_id": order.pk}),
        )
        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PAYMENT_PAID)
        self.assertEqual(order.status, Order.PENDING)

    def test_order_item_keeps_price_snapshot(self):
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )
        self.client.post(
            reverse("shop:checkout_review"),
            {
                "full_name": "Ayzal Yohan",
                "email": "ayzal@example.com",
                "phone": "",
                "shipping_address": "12 River Road",
                "shipping_city": "Dhaka",
                "shipping_postal_code": "1205",
                "shipping_country": "Bangladesh",
                "notes": "",
            },
        )
        self.client.post(reverse("shop:place_order"))

        self.active_product.price = Decimal("20.00")
        self.active_product.save(update_fields=["price", "updated_at"])

        item = OrderItem.objects.get()
        self.assertEqual(item.unit_price, Decimal("12.50"))
        self.assertEqual(item.line_total, Decimal("12.50"))

    def test_order_success_requires_the_current_session(self):
        order = Order.objects.create(
            full_name="Someone Else",
            email="other@example.com",
            shipping_address="1 Test Street",
            shipping_city="Dhaka",
            shipping_postal_code="1200",
            shipping_country="Bangladesh",
            total_amount=Decimal("0.00"),
        )

        response = self.client.get(
            reverse("shop:order_success", kwargs={"order_id": order.pk}),
        )

        self.assertEqual(response.status_code, 404)
