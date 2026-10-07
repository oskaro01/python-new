"""Product models for the ecommerce learning lab."""

from django.conf import settings
from django.db import models


class Product(models.Model):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    HYBRID = "hybrid"

    PRODUCT_TYPE_CHOICES = [
        (PHYSICAL, "Physical"),
        (DIGITAL, "Digital"),
        (HYBRID, "Physical + digital"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    weight_grams = models.PositiveIntegerField(default=0)
    digital_file = models.FileField(upload_to="digital_products/", blank=True)
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default=PHYSICAL,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active", "name"],
                name="product_active_name_idx",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def inventory_tracked(self):
        return self.product_type in {self.PHYSICAL, self.HYBRID}

    @property
    def requires_shipping(self):
        return self.product_type in {self.PHYSICAL, self.HYBRID}

    @property
    def is_available(self):
        return not self.inventory_tracked or self.stock > 0


class Order(models.Model):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    PAYMENT_PENDING = "pending"
    PAYMENT_PAID = "paid"
    PAYMENT_FAILED = "failed"

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_FAILED, "Failed"),
    ]

    INVENTORY_NOT_REQUIRED = "not_required"
    INVENTORY_PENDING = "pending"
    INVENTORY_DEDUCTED = "deducted"
    INVENTORY_UNAVAILABLE = "unavailable"

    INVENTORY_STATUS_CHOICES = [
        (INVENTORY_NOT_REQUIRED, "Not required"),
        (INVENTORY_PENDING, "Pending"),
        (INVENTORY_DEDUCTED, "Deducted"),
        (INVENTORY_UNAVAILABLE, "Unavailable"),
    ]

    FULFILLMENT_NOT_REQUIRED = "not_required"
    FULFILLMENT_READY = "ready"
    FULFILLMENT_SHIPMENT_CREATED = "shipment_created"
    FULFILLMENT_IN_TRANSIT = "in_transit"
    FULFILLMENT_OUT_FOR_DELIVERY = "out_for_delivery"
    FULFILLMENT_DELIVERED = "delivered"
    FULFILLMENT_EXCEPTION = "exception"

    FULFILLMENT_STATUS_CHOICES = [
        (FULFILLMENT_NOT_REQUIRED, "Not required"),
        (FULFILLMENT_READY, "Ready for fulfillment"),
        (FULFILLMENT_SHIPMENT_CREATED, "Shipment created"),
        (FULFILLMENT_IN_TRANSIT, "In transit"),
        (FULFILLMENT_OUT_FOR_DELIVERY, "Out for delivery"),
        (FULFILLMENT_DELIVERED, "Delivered"),
        (FULFILLMENT_EXCEPTION, "Delivery exception"),
    ]

    payment_provider = models.CharField(max_length=40, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shop_orders",
    )
    payment_reference = models.CharField(max_length=120, blank=True)
    payment_method = models.CharField(max_length=40, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    inventory_status = models.CharField(
        max_length=20,
        choices=INVENTORY_STATUS_CHOICES,
        default=INVENTORY_PENDING,
    )
    inventory_deducted_at = models.DateTimeField(null=True, blank=True)
    fulfillment_status = models.CharField(
        max_length=30,
        choices=FULFILLMENT_STATUS_CHOICES,
        default=FULFILLMENT_READY,
    )

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    shipping_address = models.CharField(max_length=200, default="")
    shipping_city = models.CharField(max_length=100, default="")
    shipping_postal_code = models.CharField(max_length=20, default="")
    shipping_country = models.CharField(max_length=80, default="")
    shipping_method = models.CharField(max_length=30, default="")
    shipping_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING,
    )
    receipt_sent_at = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    product_name = models.CharField(max_length=120)
    product_type = models.CharField(
        max_length=20,
        choices=Product.PRODUCT_TYPE_CHOICES,
        default=Product.PHYSICAL,
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    digital_file_name = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Shipment(models.Model):
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    EXCEPTION = "exception"

    STATUS_CHOICES = [
        (CREATED, "Created"),
        (IN_TRANSIT, "In transit"),
        (OUT_FOR_DELIVERY, "Out for delivery"),
        (DELIVERED, "Delivered"),
        (EXCEPTION, "Exception"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipment")
    provider = models.CharField(max_length=40)
    provider_reference = models.CharField(max_length=120, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True)
    tracking_url = models.URLField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=CREATED)
    provider_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Shipment for order #{self.order_id}"
