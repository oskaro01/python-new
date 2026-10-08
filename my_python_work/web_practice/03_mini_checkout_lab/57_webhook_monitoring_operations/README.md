# Lesson 57: Webhook Monitoring and Operations

This lesson makes provider integrations observable. Instead of wondering what
happened after a payment, we can inspect the webhook, order, background job,
and final result as one connected chain.

## What Is Logged

`WebhookEvent` records:

- provider and provider event ID
- event type
- related order
- correlation ID
- status: received, processing, succeeded, failed, or ignored
- a small safe payload summary
- processing attempts
- error message
- received and processed timestamps

The raw provider payload is deliberately not stored here. Webhook payloads can
contain personal or payment-related data; this lab records the fields needed
for debugging without turning the database into an unnecessary sensitive-data
archive.

## Connected Flow

```text
Stripe event evt_...
  correlation: 8f...
  status: succeeded
       |
       v
Order #23 -> paid
       |
       v
Receipt job -> queued -> succeeded
       |
       v
Receipt sent
```

The Admin site now has separate views for **Webhook events** and
**Background jobs**. The order page also shows the latest webhook status,
correlation ID, and receipt job status.

## Duplicate Events

Providers retry webhooks when they do not receive a successful response. The
provider event ID is unique per provider, so receiving the same event again
does not create a second payment or receipt job. The duplicate is still safe
to inspect because the original event record remains in the log.

## Failure Investigation

For a failed process, inspect these in order:

1. Webhook event status and error message.
2. Related order payment and inventory status.
3. Background job status, attempts, and last error.
4. Provider reference and event ID.
5. Whether the worker was running when the event arrived.

This is the beginning of an operations dashboard. In a larger production
system, the same correlation ID would also appear in structured server logs,
error tracking, and provider support searches.

## Local Walkthrough

1. Start the server and complete a Stripe test payment or demo payment.
2. Run `process_jobs --limit 1` to process the receipt.
3. Open the order page and inspect the Webhook and Receipt job rows.
4. Open Admin -> Webhook events to inspect the provider event.
5. Open Admin -> Background jobs to inspect attempts and correlation IDs.
6. Select a failed job and use the retry action after fixing the cause.

## What Comes Next

Lesson 58 will be the checkout lab hardening and final end-to-end review:
security, permissions, idempotency, deployment, monitoring, and the final
physical/digital order paths. After that, we move to the separate Chat Lab.
