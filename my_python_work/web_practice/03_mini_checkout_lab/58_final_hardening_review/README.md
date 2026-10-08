# Lesson 58: Final Checkout Hardening and Review

This is the final review checkpoint for the Mini Checkout Lab before we move
to the separate Chat Lab.

## Security Review

The project now verifies:

- production cannot start without `DJANGO_SECRET_KEY`
- production uses explicit allowed hosts and trusted origins
- state-changing views require POST and CSRF protection
- customers can open only their own account orders
- guest order pages require the matching checkout session
- return requests require an authenticated owner
- private digital downloads require a valid signed token and paid order
- Stripe webhook signatures are verified before processing
- duplicate provider events do not create duplicate payment or receipt work
- refunds and inventory restoration are idempotent
- physical inventory is row-locked during deduction/restoration
- provider secrets remain in environment variables, not templates or logs

## State and Integration Review

The final order flow is:

```text
Cart
  -> Order pending
  -> Payment provider / webhook
  -> Inventory deducted
  -> Receipt job queued
  -> Receipt job succeeded
  -> Shipment created
  -> Delivered
  -> Return requested (optional)
  -> Returned/refunded (optional)
```

The important provider boundaries are isolated. Stripe, Resend, and the
future Pathao/bKash adapters can be replaced without changing the core order
state machine.

## Deployment Checklist

Before a production deploy:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py check --deploy
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate --noinput
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py collectstatic --noinput
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
```

Render must have separate production values for:

- `DATABASE_URL`
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=false`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- Stripe live or sandbox keys, depending on the environment
- Resend credentials
- the worker/scheduler command for `process_jobs`

Local SQLite data, local Stripe test data, and production Postgres data are
separate environments and must not be mixed.

## Remaining Provider Work

Pathao location IDs/webhooks and bKash sandbox/webhooks remain explicitly
pending because their sandbox access was unavailable. They are integration
tasks, not missing pieces of the core checkout design.

## Transition to Chat Lab

The checkout lab now covers a complete real-world learning foundation:
catalog, cart, checkout, payment, webhooks, inventory, fulfillment, returns,
async jobs, monitoring, accounts, security, and deployment.

The next project is `04_chat_lab`, beginning with user search, conversations,
messages, and participant-only permissions. Real-time WebSockets come later,
after the ordinary request/response version is understood.
