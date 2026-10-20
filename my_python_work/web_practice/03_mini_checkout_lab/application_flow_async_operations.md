# Mini Checkout Lab: Background Jobs and Webhook Operations

Payment providers and email services are slow, remote, and able to retry. The
web request should verify enough to record the business event, enqueue slow
work, and answer quickly. A worker performs the deferred work afterward.

## The request/worker boundary

```text
payment request or webhook
  -> verify provider event
  -> update local order
  -> create idempotent BackgroundJob
  -> return provider response quickly

worker later
  -> claim queued job
  -> perform email/provider work
  -> mark succeeded or failed
  -> retry when allowed
```

This prevents a payment provider from timing out while Django waits for an
email server or another external API.

## 1. Enqueuing a receipt job

After a verified payment, the code calls:

```python
enqueue_receipt_job(
    order,
    source_event=source_event,
    correlation_id=source_event.correlation_id if source_event else "",
)
```

The helper uses `get_or_create()` with:

```text
idempotency_key = receipt-order-<order_id>
```

If a Stripe webhook is delivered twice, both deliveries point to the same
receipt job. The database's unique constraint prevents a second job row.

The job stores:

```text
job_type       = send_receipt
order          = related Order
source_event   = related WebhookEvent, if any
correlation_id = shared investigation ID
payload        = {order_id: ...}
status         = queued
attempts       = 0
max_attempts   = 3
available_at   = now
```

## 2. Claiming a job safely

`process_next_job()` opens a database transaction and selects the earliest
available queued or failed job whose attempts are below the maximum.

It uses `select_for_update()` while changing the row to:

```text
status     = running
attempts   = attempts + 1
locked_at  = now
started_at = now
```

The transaction commits before the slow email call starts. Another worker that
tries to claim at the same time cannot claim the same row during the lock.

The worker then calls `run_job(job)`. For a receipt job, it reloads the order
and stops safely if:

```text
the order is no longer paid
or receipt_sent_at is already set
```

Otherwise it renders the receipt email, sends it through the configured email
backend, and records `receipt_sent_at`.

## 3. Success and retry behavior

After `run_job()` succeeds:

```text
status       = succeeded
completed_at = now
```

If any exception occurs:

```text
status       = failed
last_error   = exception text
available_at = now + 2 ** attempts seconds
```

The next worker run can claim the failed job after its backoff. Once attempts
reach `max_attempts`, the normal query no longer selects it. Admin can inspect
the error and explicitly queue it again after fixing the cause.

This is a small educational queue, not a replacement for a durable production
queue. A future Celery, RQ, or managed queue can use the same order/job
boundary.

## 4. Running the worker

The Django management command is:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py process_jobs --limit 1
```

The command calls `process_jobs(limit=...)`, prints each final job status, and
exits. A scheduler or long-running process would execute it repeatedly in
production.

The web request does not send the receipt merely because a job exists. The
worker must claim and process it.

## 5. Webhook event lifecycle

An external provider sends a server-to-server event such as:

```text
POST /payments/stripe/webhook/
```

The webhook endpoint first validates the provider signature. Only a valid event
gets into the monitoring workflow.

For a valid event, the application creates or finds a `WebhookEvent` using:

```text
provider + provider_event_id
```

That pair is unique. The record contains a safe summary rather than the entire
raw payment payload:

```text
provider_event_id
event_type
related order
correlation_id
status
payload_summary
attempt_count
error_message
received_at
processed_at
```

The correlation ID is generated once and passed to the receipt job. It connects
the provider event, local order, background job, and operations investigation.

## 6. Webhook processing states

```text
received
  -> processing
  -> succeeded

processing -> failed
other event type -> ignored
```

When the same event arrives again after success, the endpoint returns a safe
duplicate response without paying the order or enqueueing another receipt.

When processing raises an exception, the event records the error and processed
time, then returns a failure response so the provider may retry or operations
can investigate.

## 7. Connected operational chain

```text
Stripe event evt_...
  correlation_id = abc123
  status = succeeded
       |
       v
Order #23
  payment_status = paid
       |
       v
BackgroundJob
  status = queued -> succeeded
  correlation_id = abc123
       |
       v
receipt_sent_at = timestamp
```

The order-success page shows the latest webhook and receipt-job information.
Admin provides separate searchable lists for orders, webhook events, and
background jobs.

## 8. Admin operations

Admin can inspect:

```text
Webhook events -> provider, event type, order, status, attempts, correlation
Background jobs -> job type, order, status, attempts, availability, errors
```

Failed jobs have a retry action that resets them to queued and makes them
available immediately. The provider event record remains unchanged, preserving
the original history.

## Why this separation matters

Without a job boundary:

```text
provider webhook -> send email -> timeout -> provider retries -> duplicate work
```

With the boundary:

```text
provider webhook -> verify/store/enqueue -> quick 200 response
worker -> retry email independently -> visible final state
```

The same pattern can later handle refunds, courier calls, bKash follow-up work,
and expensive webhook processing.

## Debugging checklist

```text
payment succeeds but no email -> job was not enqueued or worker not running
job stays queued              -> process_jobs was never executed
job keeps failing             -> inspect last_error and email settings
job runs twice                -> inspect idempotency key and row lock
webhook returns 400           -> provider signature or secret mismatch
duplicate event                -> expected; inspect the original event row
event succeeded, job failed   -> inspect shared correlation ID
job shows running forever     -> worker crashed after claiming; add recovery
```

## Files involved

- `shop/jobs.py`: enqueue, claim, run, retry, and complete jobs.
- `shop/management/commands/process_jobs.py`: worker command.
- `shop/emails.py`: receipt rendering and email send.
- `shop/models.py`: `BackgroundJob` and `WebhookEvent` records.
- `shop/views.py`: webhook verification and job enqueueing.
- `shop/admin.py`: operations lists and retry action.
- `shop/templates/shop/order_success.html`: customer-facing operational status.
