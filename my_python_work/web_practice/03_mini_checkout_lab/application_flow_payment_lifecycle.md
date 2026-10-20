# Mini Checkout Lab: Payment Lifecycle

The checkout flow creates an order with `payment_status=pending`. Payment is
a separate lifecycle. A provider may redirect the customer, send a webhook,
or return a callback, but only the server can mark an order paid.

## The boundary

```text
pending Order
  -> provider request
  -> customer completes payment
  -> server verifies provider result
  -> lock local order
  -> mark paid
  -> deduct inventory
  -> update fulfillment
  -> queue receipt
```

The browser's success page is not proof of payment. Provider data must be
verified and matched to the local order's amount, currency, and reference.

## Order state fields

`Order` keeps several states separate:

```text
status             -> pending, processing, completed, cancelled, returned
payment_status     -> pending, paid, failed, refunded
payment_provider   -> demo, stripe, or bkash
payment_reference  -> provider session/payment/transaction ID
payment_method     -> demo, card, or mobile_wallet
paid_at            -> server timestamp after verification
inventory_status   -> not_required, pending, deducted, unavailable, restored
fulfillment_status -> delivery or digital-fulfillment state
```

An order can be paid while still processing because shipping may not be
finished.

## 1. Local simulated payment

With no real provider configured, the success page shows a demo form:

```text
POST /orders/<order_id>/simulate-payment/
```

The view first checks `last_order_id` in the session. That prevents a visitor
from using the demo button with an arbitrary order number.

If payment is still pending, it writes:

```text
payment_status    = paid
status            = processing
payment_provider  = demo
payment_reference = demo-order-<id>
payment_method    = demo
paid_at           = current server time
```

Then it runs the common post-payment pipeline:

```text
deduct_paid_order_inventory(order)
mark_order_ready_for_fulfillment(order)
enqueue_receipt_job(order)
```

This teaches the state transition locally. It is not a real payment security
mechanism.

If the order already has a payment result, the view does not pay it again.

## 2. Inventory after payment

Inventory is deducted only after payment is marked paid. The helper first
checks whether this order was already deducted, preventing a repeated callback
from subtracting stock twice.

Digital-only orders become `inventory_status=not_required`. Physical and hybrid
orders load their products and lock them with `select_for_update()` inside a
transaction. The locked check requires every product to exist and have enough
stock.

```text
stock check fails  -> inventory_status=unavailable
stock check passes -> subtract quantities and record deduction time
```

The row lock protects the last units of stock when two paid orders arrive at
the same time.

## 3. Fulfillment and receipt job

`mark_order_ready_for_fulfillment()` converts inventory state into business
state:

```text
digital-only            -> fulfillment not_required, order completed
physical stock deducted -> fulfillment ready, order processing
stock unavailable       -> no successful fulfillment transition
```

The payment handler queues a receipt job instead of sending email directly.
`enqueue_receipt_job()` uses `receipt-order-<order_id>` as an idempotency key.
Repeated callbacks therefore reuse one job.

The worker claims jobs with a database lock, sends the receipt, records
`receipt_sent_at`, and marks the job succeeded. Failures store `last_error`
and retry with a short exponential delay until `max_attempts` is reached.

## 4. Stripe checkout start

When Stripe is configured, the order-success page submits:

```text
POST /orders/<order_id>/pay/
```

The view checks `last_order_id` and requires `payment_status=pending`. The
provider client builds Stripe line items from saved `OrderItem` snapshots and
adds shipping as another line item.

The Stripe session receives:

```text
customer_email
client_reference_id = local order ID
metadata.order_id   = local order ID
success_url         = local success page
cancel_url          = local success page
```

The local order stores the Stripe session ID, then the browser is redirected
to Stripe. The redirect itself does not mark the order paid.

## 5. Stripe webhook verification

Stripe sends a server-to-server request to:

```text
POST /payments/stripe/webhook/
```

The endpoint is CSRF-exempt because Stripe has no browser CSRF cookie. Instead,
`construct_stripe_event()` verifies the raw body using `Stripe-Signature` and
the webhook secret.

Invalid signatures return 400 and change nothing.

Valid events are stored in `WebhookEvent` using the provider event ID. The
database uniqueness constraint makes repeated delivery recognizable. A
previously succeeded event returns as a duplicate without repeating payment
logic.

Relevant events follow these paths:

```text
checkout.session.completed
checkout.session.async_payment_succeeded -> confirm_stripe_payment()
checkout.session.async_payment_failed    -> fail_stripe_payment()
other event                              -> ignored event record
```

`confirm_stripe_payment()` reads the local order ID from Stripe metadata,
requires Stripe's payment status to be paid, locks the order with
`select_for_update()`, and safely returns if the order is already paid. It then
updates payment fields and runs inventory, fulfillment, and receipt processing.

The event is marked succeeded. Exceptions mark it failed and store the error
for operations to inspect.

## 6. bKash configuration

The bKash path is enabled only when these settings exist:

```text
PAYMENT_PROVIDER=bkash
BKASH_BASE_URL
BKASH_APP_KEY
BKASH_APP_SECRET
BKASH_USERNAME
BKASH_PASSWORD
```

Secrets stay in environment variables. They never belong in templates,
JavaScript, Git, or order rows.

## 7. bKash create payment

The bKash button sends a CSRF-protected request to:

```text
POST /orders/<order_id>/pay/bkash/create/
```

The server checks the session's `last_order_id` and requires a pending order.
The provider client first requests a short-lived access token:

```text
POST /auth/grant-token
```

The token is cached in process memory until shortly before expiry. Later API
calls send it as a bearer token with `X-App-Key`.

The create request uses server-owned order values:

```text
callbackURL
payerReference
amount = order.total_amount
currency = BDT
intent = sale
merchantInvoiceNumber = order-<id>
```

The server requires a returned payment ID, stores it as `payment_reference`,
and returns bKash's response. The JavaScript redirects to the returned
`bkashURL`. The browser never receives merchant credentials.

## 8. bKash callback and execute verification

After the external bKash page, bKash redirects to:

```text
GET /payments/bkash/callback/?paymentId=...&status=success
```

The callback does not trust `status=success` alone. It:

1. Requires a payment ID.
2. Finds the local bKash order with the matching payment reference.
3. Rejects a non-success callback status.
4. Calls `POST /payment/execute` with that payment ID.
5. Validates the execution response.

`confirm_bkash_payment()` requires:

```text
transactionStatus == Completed
merchantInvoiceNumber == order-<local order ID>
currency == configured BDT
amount == order.total_amount
```

Only then does it lock the order, mark it paid, record the transaction
reference, deduct inventory, update fulfillment, and queue a receipt.

The separate Django execute endpoint also verifies that the submitted payment
ID matches the order's stored reference.

## Idempotency and race protection

Callbacks and webhooks can repeat. The code protects local state with:

```text
already paid order      -> do not apply payment twice
select_for_update()     -> serialize competing order updates
unique webhook ID       -> recognize repeated provider delivery
inventory deducted flag -> do not subtract stock twice
receipt job key         -> do not queue duplicate receipts
```

The system is designed for repeated network delivery rather than assuming one
perfect request.

## Payment state machine

```text
Order created
  payment_status=pending
       |
       +-- provider setup fails -> remains pending + error
       +-- payment fails        -> payment_status=failed
       +-- verified completion  -> payment_status=paid
                                      |
                                      +-- inventory handled
                                      +-- fulfillment updated
                                      +-- receipt queued

paid order -> refund workflow -> payment_status=refunded
```

## Debugging checklist

```text
payment button absent     -> provider setting or credentials
provider redirect fails   -> create-session/API request
return page still pending -> return is not payment proof
Stripe webhook 400        -> signature or webhook secret
duplicate webhook         -> inspect WebhookEvent status
bKash rejected            -> ID, status, amount, currency, or invoice mismatch
paid but stock unchanged  -> inventory state or lock failure
receipt not sent          -> queued BackgroundJob needs its worker
paid twice                -> missing lock or idempotency guard
```

## Files involved

- `shop/payments.py`: Stripe and bKash provider boundary.
- `shop/views.py`: demo payment, provider start, callbacks, webhook, confirmation.
- `shop/models.py`: payment, inventory, fulfillment, webhook, and job states.
- `shop/inventory.py`: locked stock deduction and restoration.
- `shop/jobs.py`: idempotent receipt queue and retries.
- `shop/templates/shop/order_success.html`: payment entry points and status.
- `shop/static/shop/bkash_checkout.js`: browser-side bKash redirect.
- `mini_checkout_lab/settings.py`: provider selection and secrets.
