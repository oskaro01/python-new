"""Admin setup for the product catalog."""

from django.contrib import admin

from .models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "product_type", "price", "stock", "is_active", "updated_at")
    list_filter = ("product_type", "is_active")
    list_editable = ("price", "stock", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = (
        "product",
        "product_name",
        "product_type",
        "unit_price",
        "quantity",
        "line_total",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "status",
        "payment_status",
        "payment_provider",
        "payment_method",
        "shipping_method",
        "shipping_amount",
        "receipt_sent_at",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "payment_status", "shipping_method", "created_at")
    search_fields = (
        "full_name",
        "email",
        "shipping_city",
        "shipping_postal_code",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "receipt_sent_at",
        "paid_at",
        "payment_provider",
        "payment_reference",
        "payment_method",
        "shipping_amount",
        "total_amount",
    )
    inlines = [OrderItemInline]
    ordering = ("-created_at",)
