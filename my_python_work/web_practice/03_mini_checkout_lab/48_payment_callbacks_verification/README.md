# Django Ecommerce 48: Payment Callbacks And Verification

This lesson completes the Stripe sandbox callback flow and makes payment state
clear to the customer.

## What We Built

- Verified `checkout.session.completed` handling for immediate payments
- Delayed-payment success handling
- Delayed-payment failure handling
- Idempotent callbacks so repeated events do not send duplicate receipts
- A prominent paid, pending, or failed payment notice on the order page
- Receipt sending only after confirmed payment

## Events

```text
checkout.session.completed
checkout.session.async_payment_succeeded
checkout.session.async_payment_failed
```

An unpaid completed session remains pending. A delayed success can later mark
it paid, while a delayed failure marks it failed. Already-paid orders are not
processed again.

## Local Listener

```powershell
stripe listen --events="checkout.session.completed,checkout.session.async_payment_succeeded,checkout.session.async_payment_failed" --forward-to="http://127.0.0.1:8001/payments/stripe/webhook/"
```

Use the signing secret printed by this listener as the local
`STRIPE_WEBHOOK_SECRET`. A deployed Stripe Dashboard endpoint has its own
stable signing secret.

## Render Webhook Events

Enable the same three events on the Stripe Dashboard endpoint connected to:

```text
https://your-checkout-domain.example/payments/stripe/webhook/
```

## Checkpoint

The application now trusts verified provider callbacks for payment state,
handles immediate and delayed results, and communicates that state clearly.

## Next Lesson

Lesson 49 connects paid physical orders to fulfillment and courier tracking.
