"""Admin setup for the product catalog."""

from django.contrib import admin

from .models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "is_active", "updated_at")
    list_filter = ("is_active",)
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
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at")
    search_fields = (
        "full_name",
        "email",
        "shipping_city",
        "shipping_postal_code",
    )
    readonly_fields = ("created_at", "updated_at", "total_amount")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)
