# Lesson 56: Background Jobs and Async Work

This lesson introduces a small database-backed worker so slow work does not
hold open a payment or webhook request.

## The Request/Worker Boundary

When a payment succeeds, the web request now does this:

```text
Stripe webhook or demo payment
  -> verify/update the order
  -> create one receipt job
  -> return a response quickly

Worker later
  -> claim queued job
  -> send the receipt
  -> mark job succeeded or failed
```

The payment provider does not wait for Resend. This matters because providers
can retry a webhook when our endpoint takes too long to respond.

## BackgroundJob

Each job records:

- job type
- related order
- idempotency key
- status: queued, running, succeeded, or failed
- attempt count and maximum attempts
- next available time
- start/completion timestamps
- the last error

Receipt jobs use one idempotency key per order, so a repeated webhook cannot
create duplicate receipt jobs.

## Run the Worker Locally

Local credentials belong in `03_mini_checkout_lab/.env`. Copy
`.env.example` to `.env`, fill in the values, and restart Django. The `.env`
file is ignored by Git and should never be committed.

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py process_jobs --limit 1
```

Run the command after completing a demo or Stripe sandbox payment. The order
page and Admin -> Background jobs will show the state change.

For a small batch:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py process_jobs --limit 10
```

In production, a scheduler or long-running worker would execute this command
repeatedly. Later we can replace this educational worker with Celery, RQ, or a
managed queue without changing the order/payment boundary.

## Retry Behavior

If sending the email raises an exception:

1. The job becomes `failed`.
2. The error is stored for inspection.
3. The attempt count increases.
4. It becomes available again after a short backoff.
5. It stops retrying after the configured maximum attempts.

The Admin job list can requeue a failed job manually. In production, retry
limits and alerting would be configured more carefully.

## Why This Is Related to Webhooks

They solve different sides of the integration:

- A webhook is an incoming provider event.
- A background job is work our application defers.

The safe pattern is to verify and store the webhook quickly, then enqueue the
slow follow-up work. This same pattern will later handle receipt emails,
refund calls, courier API calls, and webhook event processing.

## Next Lesson

Lesson 57 will add durable webhook event logs, job history, correlation IDs,
and an operations view for seeing exactly which step is pending or complete.
