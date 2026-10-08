"""Small database-backed background job queue for the learning lab."""

from datetime import timedelta

from django.db import models, transaction
from django.utils import timezone

from .emails import send_order_receipt
from .models import BackgroundJob, Order


def enqueue_receipt_job(order):
    """Create one receipt job for an order, even if called repeatedly."""

    job, _ = BackgroundJob.objects.get_or_create(
        idempotency_key=f"receipt-order-{order.pk}",
        defaults={
            "job_type": BackgroundJob.SEND_RECEIPT,
            "order": order,
            "payload": {"order_id": order.pk},
        },
    )
    return job


def run_job(job):
    """Run the supported job type. Add handlers here as the system grows."""

    if job.job_type != BackgroundJob.SEND_RECEIPT:
        raise ValueError(f"Unsupported background job: {job.job_type}")

    order = Order.objects.get(pk=job.order_id)
    if order.payment_status != Order.PAYMENT_PAID or order.receipt_sent_at:
        return
    send_order_receipt(order)
    order.receipt_sent_at = timezone.now()
    order.save(update_fields=["receipt_sent_at", "updated_at"])


def process_next_job():
    """Claim and process the next available job, returning it or None."""

    now = timezone.now()
    with transaction.atomic():
        job = (
            BackgroundJob.objects.select_for_update()
            .filter(
                status__in=[BackgroundJob.QUEUED, BackgroundJob.FAILED],
                attempts__lt=models.F("max_attempts"),
                available_at__lte=now,
            )
            .order_by("available_at", "created_at")
            .first()
        )
        if not job:
            return None
        job.status = BackgroundJob.RUNNING
        job.attempts += 1
        job.locked_at = now
        job.started_at = now
        job.last_error = ""
        job.save(
            update_fields=[
                "status",
                "attempts",
                "locked_at",
                "started_at",
                "last_error",
                "updated_at",
            ]
        )

    try:
        run_job(job)
    except Exception as error:
        job.status = BackgroundJob.FAILED
        job.last_error = str(error)
        job.available_at = timezone.now() + timedelta(seconds=2 ** job.attempts)
        job.save(update_fields=["status", "last_error", "available_at", "updated_at"])
    else:
        job.status = BackgroundJob.SUCCEEDED
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "completed_at", "updated_at"])
    return job


def process_jobs(limit=1):
    """Process at most ``limit`` jobs and return their final records."""

    processed = []
    for _ in range(limit):
        job = process_next_job()
        if not job:
            break
        processed.append(job)
    return processed
