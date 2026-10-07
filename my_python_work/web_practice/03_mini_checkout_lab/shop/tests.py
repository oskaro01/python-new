from decimal import Decimal
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .downloads import create_download_token
from .models import Order, OrderItem, Product, Shipment
from .shipping import create_shipment_for_order, update_shipment_status


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

    def test_digital_product_with_zero_stock_can_be_added(self):
        digital_product = Product.objects.create(
            name="Pixel Wallpaper",
            slug="pixel-wallpaper",
            description="A downloadable wallpaper.",
            price=Decimal("4.99"),
            product_type=Product.DIGITAL,
            stock=0,
        )

        response = self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": digital_product.pk}),
        )

        self.assertRedirects(response, reverse("shop:product_list"))
        self.assertEqual(self.client.session["cart"], {str(digital_product.pk): 1})

    def test_physical_product_with_zero_stock_cannot_be_added(self):
        self.active_product.stock = 0
        self.active_product.save(update_fields=["stock", "updated_at"])

        response = self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )

        self.assertRedirects(response, reverse("shop:product_list"))
        self.assertNotIn("cart", self.client.session)

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

    def test_state_changing_endpoints_require_post(self):
        endpoints = [
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
            reverse("shop:update_cart", kwargs={"product_id": self.active_product.pk}),
            reverse("shop:remove_from_cart", kwargs={"product_id": self.active_product.pk}),
            reverse("shop:checkout_review"),
            reverse("shop:place_order"),
            reverse("shop:simulate_payment", kwargs={"order_id": 1}),
            reverse("shop:start_payment", kwargs={"order_id": 1}),
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.client.get(endpoint).status_code, 405)

    def test_csrf_protects_add_to_cart(self):
        client = Client(enforce_csrf_checks=True)

        response = client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": self.active_product.pk}),
        )

        self.assertEqual(response.status_code, 403)

    def test_security_headers_are_present(self):
        response = self.client.get(reverse("shop:product_list"))

        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")

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
                "shipping_method": "standard",
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
                "shipping_method": "standard",
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
        self.assertEqual(order.total_amount, Decimal("17.50"))
        self.assertEqual(order.shipping_method, "standard")
        self.assertEqual(order.shipping_amount, Decimal("5.00"))
        self.assertEqual(order.shipping_address, "12 River Road")
        self.assertEqual(order.shipping_city, "Dhaka")
        self.assertEqual(order.shipping_postal_code, "1205")
        self.assertEqual(order.shipping_country, "Bangladesh")
        self.assertEqual(item.product_name, "Canvas Tote")
        self.assertEqual(item.product_type, Product.PHYSICAL)
        self.assertEqual(item.unit_price, Decimal("12.50"))
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.line_total, Decimal("12.50"))
        self.assertNotIn("cart", self.client.session)
        self.assertNotIn("checkout_customer", self.client.session)

    def test_digital_only_checkout_does_not_require_shipping(self):
        self.active_product.delete()
        digital_product = Product.objects.create(
            name="Digital Guide",
            slug="digital-guide",
            description="A downloadable guide.",
            price=Decimal("3.00"),
            product_type=Product.DIGITAL,
            stock=0,
        )
        self.client.post(
            reverse("shop:add_to_cart", kwargs={"product_id": digital_product.pk}),
        )

        response = self.client.post(
            reverse("shop:checkout_review"),
            {
                "full_name": "Ayzal Yohan",
                "email": "ayzal@example.com",
                "phone": "",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Place order")
        self.assertNotContains(response, "Shipping address<br>")

        self.client.post(reverse("shop:place_order"))
        order = Order.objects.get()
        item = OrderItem.objects.get(order=order)
        self.assertEqual(order.shipping_address, "")
        self.assertEqual(item.product_type, Product.DIGITAL)

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
                "shipping_method": "standard",
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
        self.assertEqual(order.inventory_status, Order.INVENTORY_DEDUCTED)
        self.active_product.refresh_from_db()
        self.assertEqual(self.active_product.stock, 3)
        self.assertEqual(order.status, Order.PROCESSING)
        self.assertIsNotNone(order.receipt_sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ayzal@example.com"])
        self.assertIn(f"Order #{order.pk}", mail.outbox[0].subject)
        self.assertIn("Canvas Tote x 1", mail.outbox[0].body)

        self.client.post(
            reverse("shop:simulate_payment", kwargs={"order_id": order.pk}),
        )
        self.assertEqual(len(mail.outbox), 1)

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
                "shipping_method": "standard",
                "notes": "",
            },
        )
        self.client.post(reverse("shop:place_order"))

        self.active_product.price = Decimal("20.00")
        self.active_product.save(update_fields=["price", "updated_at"])

        item = OrderItem.objects.get()
        self.assertEqual(item.unit_price, Decimal("12.50"))
        self.assertEqual(item.line_total, Decimal("12.50"))

    def test_start_payment_saves_provider_checkout_reference(self):
        order = Order.objects.create(
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            total_amount=Decimal("12.50"),
        )
        OrderItem.objects.create(
            order=order,
            product=self.active_product,
            product_name=self.active_product.name,
            unit_price=self.active_product.price,
            quantity=1,
            line_total=self.active_product.price,
        )
        session = self.client.session
        session["last_order_id"] = order.pk
        session.save()

        provider_session = SimpleNamespace(
            id="cs_test_checkout_123",
            url="https://checkout.stripe.test/session/123",
        )
        with patch(
            "shop.views.create_stripe_checkout_session",
            return_value=provider_session,
        ):
            response = self.client.post(
                reverse("shop:start_payment", kwargs={"order_id": order.pk})
            )

        self.assertRedirects(
            response,
            provider_session.url,
            fetch_redirect_response=False,
        )
        order.refresh_from_db()
        self.assertEqual(order.payment_provider, "stripe")
        self.assertEqual(order.payment_reference, provider_session.id)
        self.assertEqual(order.payment_method, "card")
        self.assertEqual(order.payment_status, Order.PAYMENT_PENDING)

    def test_paid_stripe_webhook_confirms_order_once(self):
        order = Order.objects.create(
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            total_amount=Decimal("12.50"),
        )
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_checkout_123",
                    "payment_intent": "pi_test_123",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order.pk)},
                }
            },
        }

        with patch("shop.views.construct_stripe_event", return_value=event):
            first_response = self.client.post(
                reverse("shop:stripe_webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )
            second_response = self.client.post(
                reverse("shop:stripe_webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PAYMENT_PAID)
        self.assertEqual(order.payment_provider, "stripe")
        self.assertEqual(order.payment_reference, "pi_test_123")
        self.assertIsNotNone(order.paid_at)
        self.assertIsNotNone(order.receipt_sent_at)
        self.assertEqual(len(mail.outbox), 1)

    def test_async_stripe_success_confirms_pending_order(self):
        order = Order.objects.create(
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            total_amount=Decimal("12.50"),
        )
        event = {
            "type": "checkout.session.async_payment_succeeded",
            "data": {
                "object": {
                    "id": "cs_test_async_123",
                    "payment_intent": "pi_test_async_123",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order.pk)},
                }
            },
        }

        with patch("shop.views.construct_stripe_event", return_value=event):
            response = self.client.post(
                reverse("shop:stripe_webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PAYMENT_PAID)
        self.assertEqual(order.inventory_status, Order.INVENTORY_NOT_REQUIRED)
        self.assertEqual(order.payment_reference, "pi_test_async_123")
        self.assertEqual(len(mail.outbox), 1)

    def test_async_stripe_failure_marks_pending_order_failed(self):
        order = Order.objects.create(
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            total_amount=Decimal("12.50"),
        )
        event = {
            "type": "checkout.session.async_payment_failed",
            "data": {
                "object": {
                    "id": "cs_test_async_456",
                    "payment_intent": "pi_test_async_456",
                    "payment_status": "unpaid",
                    "metadata": {"order_id": str(order.pk)},
                }
            },
        }

        with patch("shop.views.construct_stripe_event", return_value=event):
            response = self.client.post(
                reverse("shop:stripe_webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PAYMENT_FAILED)
        self.assertEqual(order.payment_reference, "pi_test_async_456")
        self.assertIsNone(order.receipt_sent_at)
        self.assertEqual(len(mail.outbox), 0)

    def test_paid_order_cannot_deduct_more_stock_when_webhook_repeats(self):
        self.active_product.stock = 1
        self.active_product.save(update_fields=["stock", "updated_at"])
        order = Order.objects.create(
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            total_amount=Decimal("12.50"),
        )
        OrderItem.objects.create(
            order=order,
            product=self.active_product,
            product_name=self.active_product.name,
            product_type=Product.PHYSICAL,
            unit_price=self.active_product.price,
            quantity=1,
            line_total=self.active_product.price,
        )
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_inventory_123",
                    "payment_intent": "pi_test_inventory_123",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order.pk)},
                }
            },
        }

        with patch("shop.views.construct_stripe_event", return_value=event):
            self.client.post(
                reverse("shop:stripe_webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )
            self.client.post(
                reverse("shop:stripe_webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        order.refresh_from_db()
        self.active_product.refresh_from_db()
        self.assertEqual(order.inventory_status, Order.INVENTORY_DEDUCTED)
        self.assertEqual(self.active_product.stock, 0)

    def test_order_page_highlights_confirmed_payment(self):
        order = Order.objects.create(
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            payment_status=Order.PAYMENT_PAID,
            total_amount=Decimal("12.50"),
        )
        session = self.client.session
        session["last_order_id"] = order.pk
        session.save()

        response = self.client.get(
            reverse("shop:order_success", kwargs={"order_id": order.pk})
        )

        self.assertContains(response, "Payment confirmed")
        self.assertContains(response, "payment-confirmation-success")

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


class FulfillmentTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Canvas Tote",
            slug="canvas-tote-fulfillment",
            price=Decimal("12.50"),
            stock=2,
        )
        self.order = Order.objects.create(
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            shipping_address="12 River Road",
            shipping_city="Dhaka",
            shipping_postal_code="1205",
            shipping_country="Bangladesh",
            payment_status=Order.PAYMENT_PAID,
            inventory_status=Order.INVENTORY_DEDUCTED,
            fulfillment_status=Order.FULFILLMENT_READY,
            total_amount=Decimal("17.50"),
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            product_type=Product.PHYSICAL,
            unit_price=self.product.price,
            quantity=1,
            line_total=self.product.price,
        )

    def test_paid_ready_order_gets_one_sandbox_shipment(self):
        shipment = create_shipment_for_order(self.order)

        self.assertEqual(shipment.provider, "manual")
        self.assertEqual(shipment.tracking_number, f"DEMO-{self.order.pk:06d}")
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.fulfillment_status,
            Order.FULFILLMENT_SHIPMENT_CREATED,
        )
        self.assertEqual(create_shipment_for_order(self.order).pk, shipment.pk)
        self.assertEqual(Shipment.objects.count(), 1)

    def test_shipment_status_updates_order_and_timestamps(self):
        shipment = create_shipment_for_order(self.order)

        update_shipment_status(shipment, Shipment.IN_TRANSIT)
        shipment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertIsNotNone(shipment.shipped_at)
        self.assertEqual(self.order.fulfillment_status, Order.FULFILLMENT_IN_TRANSIT)

        update_shipment_status(shipment, Shipment.DELIVERED)
        shipment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertIsNotNone(shipment.delivered_at)
        self.assertEqual(self.order.fulfillment_status, Order.FULFILLMENT_DELIVERED)
        self.assertEqual(self.order.status, Order.COMPLETED)


class SecureDigitalFulfillmentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_directory = tempfile.TemporaryDirectory()
        cls.media_override = override_settings(MEDIA_ROOT=cls.media_directory.name)
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        cls.media_directory.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.product = Product.objects.create(
            name="Digital Guide",
            slug="secure-digital-guide",
            price=Decimal("4.00"),
            product_type=Product.DIGITAL,
            digital_file=SimpleUploadedFile(
                "guide.txt",
                b"Private paid content",
                content_type="text/plain",
            ),
        )
        self.order = Order.objects.create(
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            payment_status=Order.PAYMENT_PAID,
            total_amount=Decimal("4.00"),
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            product_type=Product.DIGITAL,
            unit_price=self.product.price,
            quantity=1,
            line_total=self.product.price,
            digital_file_name=self.product.digital_file.name,
        )

    def download_url(self, token=None):
        token = token or create_download_token(self.item)
        return (
            reverse(
                "shop:download_order_item",
                kwargs={"order_id": self.order.pk, "item_id": self.item.pk},
            )
            + f"?token={token}"
        )

    def test_paid_customer_can_download_the_private_file(self):
        response = self.client.get(self.download_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"Private paid content")
        self.assertIn("attachment", response.headers["Content-Disposition"])

    def test_unpaid_order_cannot_download(self):
        self.order.payment_status = Order.PAYMENT_PENDING
        self.order.save(update_fields=["payment_status", "updated_at"])

        response = self.client.get(self.download_url())

        self.assertEqual(response.status_code, 404)

    def test_modified_token_is_rejected(self):
        response = self.client.get(self.download_url(token="not-a-valid-token"))

        self.assertEqual(response.status_code, 404)


class AccountOrderHistoryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="ayzal",
            email="ayzal@example.com",
            password="Strong-test-password-123",
        )
        self.order = Order.objects.create(
            customer=self.user,
            full_name="Ayzal Yohan",
            email="ayzal@example.com",
            total_amount=Decimal("4.00"),
        )

    def test_user_can_register(self):
        response = self.client.post(
            reverse("shop:register"),
            {
                "username": "new-customer",
                "email": "new@example.com",
                "password1": "Strong-test-password-123",
                "password2": "Strong-test-password-123",
            },
        )

        self.assertRedirects(response, reverse("shop:product_list"))
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_authenticated_customer_sees_only_owned_orders(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("shop:order_history"))

        self.assertContains(response, f"Order #{self.order.pk}")

    def test_authenticated_owner_can_reopen_order_page(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("shop:order_success", kwargs={"order_id": self.order.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Order status")

    def test_guest_is_redirected_from_order_history(self):
        response = self.client.get(reverse("shop:order_history"))

        self.assertRedirects(
            response,
            f"/accounts/login/?next={reverse('shop:order_history')}",
        )
