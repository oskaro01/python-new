"""Product models for the ecommerce learning lab."""

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
    PAID = "paid"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PAID, "Paid"),
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

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    shipping_address = models.CharField(max_length=200, default="")
    shipping_city = models.CharField(max_length=100, default="")
    shipping_postal_code = models.CharField(max_length=20, default="")
    shipping_country = models.CharField(max_length=80, default="")
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

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
