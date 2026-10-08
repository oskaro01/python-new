"""Admin setup for the product catalog."""

from django.contrib import admin
from django.utils import timezone

from .models import BackgroundJob, Order, OrderItem, Product, ReturnRequest, Shipment
from .refunds import CancellationNotAllowed, cancel_order
from .returns import (
    ReturnTransitionError,
    approve_return,
    complete_return,
    mark_return_in_transit,
    mark_return_received,
    reject_return,
)
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


class ReturnRequestInline(admin.StackedInline):
    model = ReturnRequest
    extra = 0
    can_delete = False
    readonly_fields = (
        "reason",
        "status",
        "review_notes",
        "pickup_provider",
        "pickup_reference",
        "tracking_number",
        "requested_at",
        "reviewed_at",
        "received_at",
        "completed_at",
        "updated_at",
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
    inlines = [OrderItemInline, ShipmentInline, ReturnRequestInline]
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


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "status",
        "pickup_provider",
        "tracking_number",
        "requested_at",
        "updated_at",
    )
    list_filter = ("status", "pickup_provider", "requested_at")
    search_fields = ("order__email", "order__full_name", "tracking_number")
    readonly_fields = (
        "order",
        "reason",
        "status",
        "pickup_provider",
        "pickup_reference",
        "tracking_number",
        "requested_at",
        "reviewed_at",
        "received_at",
        "completed_at",
        "updated_at",
    )
    actions = (
        "approve_selected_returns",
        "reject_selected_returns",
        "mark_selected_in_transit",
        "mark_selected_received",
        "refund_selected_returns",
    )

    def _run_transition(self, request, queryset, transition, success_message):
        changed = 0
        for return_request in queryset:
            try:
                transition(return_request)
            except (ReturnTransitionError, RuntimeError, ValueError) as error:
                self.message_user(
                    request,
                    f"Order #{return_request.order_id}: {error}",
                    level="WARNING",
                )
            else:
                changed += 1
        self.message_user(request, success_message.format(count=changed))

    @admin.action(description="Approve selected return requests")
    def approve_selected_returns(self, request, queryset):
        self._run_transition(
            request,
            queryset,
            approve_return,
            "Approved {count} return request(s).",
        )

    @admin.action(description="Reject selected return requests")
    def reject_selected_returns(self, request, queryset):
        self._run_transition(
            request,
            queryset,
            reject_return,
            "Rejected {count} return request(s).",
        )

    @admin.action(description="Mark selected returns in transit")
    def mark_selected_in_transit(self, request, queryset):
        self._run_transition(
            request,
            queryset,
            mark_return_in_transit,
            "Marked {count} return(s) in transit.",
        )

    @admin.action(description="Mark selected returns received")
    def mark_selected_received(self, request, queryset):
        self._run_transition(
            request,
            queryset,
            mark_return_received,
            "Marked {count} return(s) received.",
        )

    @admin.action(description="Refund and restock selected received returns")
    def refund_selected_returns(self, request, queryset):
        self._run_transition(
            request,
            queryset,
            complete_return,
            "Refunded and restocked {count} return(s).",
        )


@admin.register(BackgroundJob)
class BackgroundJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job_type",
        "order",
        "status",
        "attempts",
        "available_at",
        "completed_at",
        "updated_at",
    )
    list_filter = ("job_type", "status", "created_at")
    search_fields = ("idempotency_key", "order__email", "last_error")
    readonly_fields = (
        "job_type",
        "order",
        "idempotency_key",
        "payload",
        "status",
        "attempts",
        "max_attempts",
        "available_at",
        "locked_at",
        "started_at",
        "completed_at",
        "last_error",
        "created_at",
        "updated_at",
    )
    actions = ["retry_selected_jobs"]

    @admin.action(description="Retry selected failed jobs now")
    def retry_selected_jobs(self, request, queryset):
        changed = queryset.filter(status=BackgroundJob.FAILED).update(
            status=BackgroundJob.QUEUED,
            available_at=timezone.now(),
            last_error="",
        )
        self.message_user(request, f"Queued {changed} failed job(s) for retry.")
