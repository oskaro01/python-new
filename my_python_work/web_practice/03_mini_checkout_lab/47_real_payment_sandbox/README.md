# Django Ecommerce 47: Real Payment Sandbox

This lesson replaces the direct demo payment action with a production-shaped
payment boundary. The provider uses test credentials, so no real money moves.

## What We Built

- Payment provider, method, reference, and paid timestamp on `Order`
- Stripe Checkout Session creation behind a provider boundary
- Signed Stripe webhook endpoint
- Idempotent payment confirmation: a paid order is not paid twice
- Receipt sending after verified payment confirmation
- Demo payment retained when Stripe test credentials are absent

## Payment Flow

```text
Order pending
  -> create Stripe Checkout Session
  -> customer pays in Stripe test mode
  -> Stripe sends checkout.session.completed webhook
  -> Django verifies the signature
  -> Order becomes paid
  -> receipt is sent
```

The browser return page is not trusted as proof of payment. The webhook is the
authoritative payment confirmation.

## Environment Variables

```text
PAYMENT_PROVIDER=stripe
PAYMENT_CURRENCY=usd
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

Do not commit these values. Local development can omit them and continue using
the clearly labelled demo payment path.

## Routes

```text
POST /orders/<id>/pay/
POST /payments/stripe/webhook/
```

The webhook must be configured in the provider dashboard with the public URL:

```text
https://your-domain.example/payments/stripe/webhook/
```

## Verify

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py check
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
```

## Not Yet Built

This lesson does not deduct stock or create a courier shipment yet. Those
actions belong after verified payment in the fulfillment lesson. Refunds,
failed payments, expired sessions, and payment reconciliation also need their
own explicit handling.

## Next Lesson

Lesson 48 connects paid physical orders to a courier/fulfillment provider.
