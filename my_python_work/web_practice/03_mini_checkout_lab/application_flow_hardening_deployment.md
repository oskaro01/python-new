# Mini Checkout Lab: Hardening and Deployment Review

This is the final review of the checkout application as a system. Hardening
does not add one new customer feature; it verifies that every boundary remains
safe when requests are repeated, credentials are missing, services fail, or
the app moves from SQLite to production infrastructure.

## The final business chain

```text
catalog
  -> session cart
  -> validated checkout
  -> pending Order + OrderItems
  -> verified payment
  -> locked inventory
  -> digital delivery or shipment
  -> receipt job
  -> delivered/completed order
  -> optional cancellation, refund, or return
```

Each transition is represented by database state. The system should never
infer “paid,” “delivered,” or “refunded” only from a browser URL.

## 1. Request and mutation protections

State-changing actions use POST and CSRF protection:

```text
add/update/remove cart
checkout review/place order
register/logout
start payment
cancel order
request return
simulate payment
```

GET remains appropriate for catalog pages, cart display, order display, and
download requests whose authorization is handled by a signed token.

The Stripe webhook is the deliberate exception to normal CSRF checks. A
provider cannot send the site's browser CSRF cookie, so the endpoint is
CSRF-exempt but verifies Stripe's signed webhook payload instead.

## 2. Identity and ownership review

The application uses several independent ownership checks:

```text
guest success page     -> matching last_order_id session
customer success page  -> order.customer_id == request.user.id
order history          -> QuerySet filtered by customer=request.user
return request         -> authenticated owner query
payment start          -> matching last_order_id session
digital download      -> signed token + order/item/payment checks
```

A numeric order ID is never treated as a secret. Every order-facing action
must still apply the appropriate session or customer boundary.

## 3. Input, money, and file safety

The server recalculates important values:

```text
cart prices       -> Product rows, not hidden browser fields
shipping amount   -> shipping_cost() on the server
order total       -> Decimal subtotal + server shipping
payment amount    -> saved Order.total_amount
```

Money uses `Decimal` and database decimal fields rather than floating-point
arithmetic.

Uploads and downloads have separate protections. Digital product files remain
in private storage, and downloads require a signed expiring token, a matching
order/item, a paid order, and a valid stored filename.

## 4. Idempotency and concurrency

External systems can retry and users can double-click. The application uses:

```text
transaction.atomic()       -> grouped database changes
select_for_update()        -> row locks for orders, products, shipments, returns
unique webhook event       -> duplicate provider delivery detection
receipt-order key          -> one receipt job per order
order refund key           -> stable Stripe refund request
inventory status guard     -> no second stock deduction/restoration
one-to-one Shipment        -> no second shipment for one order
```

The hardening question is always: “What happens if this request arrives twice,
or two workers handle it at once?”

## 5. Provider boundaries

Provider-specific code is isolated behind adapters:

```text
payments.py  -> Stripe and bKash payment/refund calls
shipping.py  -> manual and Pathao shipment creation
email backend -> console or Resend delivery
jobs.py       -> local worker boundary
```

The order state machine does not need to know every provider's HTTP payload.
Provider credentials stay in environment variables and provider responses are
matched against local order data before state changes.

The manual courier and demo payment providers remain useful because tests and
local practice do not create real charges or consignments.

## 6. Environment and production settings

Local development uses:

```text
SQLite
console email backend
DEBUG=true
HTTP localhost cookies
manual fulfillment
```

Production should use separate values for:

```text
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<long random secret>
DJANGO_ALLOWED_HOSTS=<real hostname>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<real hostname>
DATABASE_URL=<checkout Postgres>
RESEND_API_KEY=<private key>
RESEND_FROM_EMAIL=<verified sender>
```

Provider settings such as Stripe, bKash, and Pathao must be configured only
when that provider is intentionally enabled. The checkout service has its own
database and environment; it must not accidentally reuse the Dictionary or
Chat service database.

## 7. HTTPS and browser security

Production settings can enforce:

```text
SECURE_SSL_REDIRECT
SESSION_COOKIE_SECURE
CSRF_COOKIE_SECURE
HSTS headers
X-Content-Type-Options
same-origin referrer policy
same-origin cross-origin opener policy
X-Frame-Options: DENY
```

HTTPS-only cookies must remain disabled for ordinary HTTP localhost practice,
otherwise the browser will not send them during local development.

`check --deploy` helps detect unsafe production settings, but it does not
prove that payment credentials, storage permissions, provider webhooks, or
database backups are correct.

## 8. Test boundary coverage

The checkout test suite protects behavior rather than only individual helper
functions. Important groups include:

```text
active/inactive product catalog
digital versus physical stock behavior
cart quantity limits and cleanup
checkout validation and totals
order and item creation
guest and authenticated order access
payment/webhook confirmation
duplicate webhook and inventory safety
shipment and tracking transitions
download token expiry and payment checks
cancellation/refund/return transitions
background job success and retry
security headers and CSRF
```

A passing test suite is evidence about the covered boundaries; it is not proof
that a real provider sandbox or production email account is configured.

## 9. Deployment sequence

Before accepting production traffic:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py check --deploy
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate --noinput
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py collectstatic --noinput
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
```

The hosted service needs a build/install step from `requirements.txt`, a
Gunicorn WSGI start command, and migrations during release/deploy. Static
files use WhiteNoise in production.

The worker must also run separately and repeatedly:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py process_jobs --limit 10
```

A web process alone cannot process queued receipts.

## 10. Production storage boundaries

PostgreSQL stores structured rows, not necessarily uploaded files. The local
`private_media/` directory is convenient for learning but an ephemeral host
filesystem is unsafe for permanent digital products.

Production digital fulfillment should use private object storage, then keep
the same Django storage API or issue short-lived provider URLs. Backups should
cover the database and the private object store separately.

## 11. Health and operations checklist

After deployment, verify:

```text
health endpoint reaches database
catalog loads with static CSS
registration/login works over HTTPS
checkout creates the expected order and item rows
provider webhook reaches the public endpoint
worker changes queued jobs to succeeded
private download rejects unpaid/expired tokens
manual shipment transitions update the order
logs do not contain secrets or full payment payloads
```

When a payment looks wrong, inspect in order:

```text
provider event ID/signature
WebhookEvent status and correlation ID
Order payment/inventory state
BackgroundJob attempts and last_error
provider reference and external dashboard
```

## Final hardening flow

```text
code change
  -> tests
  -> check --deploy
  -> migration review
  -> collectstatic
  -> production environment review
  -> release/migrate
  -> health check
  -> provider test event
  -> worker verification
  -> monitored live flow
```

## Remaining integration limits

The core checkout state machine is complete. Provider-specific work remains
separate:

```text
Pathao location IDs and webhook details -> provider account/sandbox access
bKash sandbox completion               -> merchant credentials and callbacks
private production media               -> object-storage setup
```

These are integration and operations tasks, not missing concepts in the core
catalog-to-order design.

## Files involved

- `mini_checkout_lab/settings.py`: production switches and environment values.
- `requirements.txt`: deployable dependencies.
- `shop/tests.py`: behavior and security boundary tests.
- `shop/payments.py`, `shipping.py`, `jobs.py`: provider/worker boundaries.
- `shop/models.py`: durable state and idempotency constraints.
- `shop/views.py`: request authorization and state transitions.
- `manage.py`: check, migrate, collectstatic, test, and worker commands.
