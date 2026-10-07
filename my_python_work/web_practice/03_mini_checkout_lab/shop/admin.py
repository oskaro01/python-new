"""Admin setup for the product catalog."""

from django.contrib import admin

from .models import Order, OrderItem, Product, Shipment
from .refunds import CancellationNotAllowed, cancel_order
from .shipping import create_shipment_for_order, update_shipment_status


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "product_type",
        "price",
        "stock",
        "weight_grams",
        "is_active",
        "updated_at",
    )
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
        "digital_file_name",
    )


class ShipmentInline(admin.StackedInline):
    model = Shipment
    extra = 0
    readonly_fields = (
        "provider",
        "provider_reference",
        "tracking_number",
        "tracking_url",
        "provider_payload",
        "created_at",
        "updated_at",
        "shipped_at",
        "delivered_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "full_name",
        "email",
        "status",
        "payment_status",
        "payment_provider",
        "payment_method",
        "refund_reference",
        "inventory_status",
        "fulfillment_status",
        "shipping_method",
        "shipping_amount",
        "receipt_sent_at",
        "total_amount",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "inventory_status",
        "fulfillment_status",
        "shipping_method",
        "created_at",
    )
    search_fields = (
        "full_name",
        "email",
        "customer__username",
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
        "refund_reference",
        "inventory_status",
        "inventory_deducted_at",
        "fulfillment_status",
        "shipping_amount",
        "total_amount",
    )
    inlines = [OrderItemInline, ShipmentInline]
    actions = ["create_sandbox_shipments", "cancel_selected_orders"]
    ordering = ("-created_at",)

    @admin.action(description="Create sandbox shipment for paid orders")
    def create_sandbox_shipments(self, request, queryset):
        created = 0
        for order in queryset:
            already_exists = Shipment.objects.filter(order=order).exists()
            try:
                shipment = create_shipment_for_order(order)
            except (RuntimeError, ValueError) as error:
                self.message_user(request, f"Order #{order.pk}: {error}", level="WARNING")
            else:
                if not already_exists:
                    created += 1
        self.message_user(request, f"Created {created} sandbox shipment(s).")

    @admin.action(description="Cancel selected orders and refund when eligible")
    def cancel_selected_orders(self, request, queryset):
        cancelled = 0
        for order in queryset:
            try:
                cancel_order(order, "Cancelled by admin")
            except (CancellationNotAllowed, RuntimeError, ValueError) as error:
                self.message_user(
                    request,
                    f"Order #{order.pk}: {error}",
                    level="WARNING",
                )
            else:
                cancelled += 1
        self.message_user(request, f"Cancelled {cancelled} order(s).")


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "tracking_number", "status", "updated_at")
    list_filter = ("provider", "status")
    search_fields = ("tracking_number", "provider_reference", "order__email")
    readonly_fields = (
        "order",
        "provider",
        "provider_reference",
        "tracking_number",
        "tracking_url",
        "provider_payload",
        "created_at",
        "updated_at",
        "shipped_at",
        "delivered_at",
    )

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = Shipment.objects.get(pk=obj.pk).status
        super().save_model(request, obj, form, change)
        if old_status != obj.status:
            update_shipment_status(obj, obj.status)
