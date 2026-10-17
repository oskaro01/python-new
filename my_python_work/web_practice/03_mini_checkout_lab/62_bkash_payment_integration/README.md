# Django Ecommerce 62: bKash Payment Integration

This lesson adds a server-side bKash Tokenized V2 payment boundary beside the
existing Stripe integration. It uses the one-time “Without Agreement” flow.
The application keeps the demo payment available until real bKash sandbox
credentials are configured.

## What happens

```text
Order pending
  -> customer clicks Pay with bKash
  -> browser asks Django to create a payment
  -> Django grants a short-lived bKash token
  -> Django creates the payment and returns the provider response
  -> browser redirects to bKash's hosted payment page
  -> bKash redirects to Django's callback URL
  -> Django executes the payment
  -> Django verifies Completed, invoice, amount, and currency
  -> Order becomes paid
  -> inventory and receipt work continue
```

The browser does not mark an order paid. Django executes the payment and checks
the returned transaction before changing the order state.

The backend flow follows the current bKash Tokenized V2 documentation: grant a
token, create a payment with a callback URL, execute it after the callback,
and verify the completed response. We do not create or store an agreement for
this one-time order flow. See the [bKash developer portal](https://developer.bka.sh/reference).

## Configuration

Copy the values into the checkout lab's local `.env` file after bKash sandbox
onboarding. Do not put these credentials in JavaScript, templates, Git, or
Render logs.

```env
PAYMENT_PROVIDER=bkash
BKASH_BASE_URL=https://tokenized.sandbox.bka.sh/v2/tokenized-checkout
BKASH_APP_KEY=your-sandbox-app-key
BKASH_APP_SECRET=your-sandbox-app-secret
BKASH_USERNAME=your-sandbox-username
BKASH_PASSWORD=your-sandbox-password
BKASH_CURRENCY=BDT
BKASH_TIMEOUT=30
```

If `PAYMENT_PROVIDER=bkash` is not configured completely, the order page keeps
showing the safe demo payment button instead.

## Routes

```text
POST /orders/<id>/pay/bkash/create/
GET  /payments/bkash/callback/
POST /orders/<id>/pay/bkash/execute/  (manual verification route)
```

The create route requires the checkout session and CSRF protection. The
callback does not trust the returned status by itself: it calls bKash Execute
Payment and checks the returned transaction, invoice, amount, and currency
before changing the order state.

## Local verification

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py check
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py collectstatic --noinput
```

Use sandbox credentials only for the first real checkout test. Keep the demo
provider available while the account, callback behavior, and sandbox test
wallet are being verified.

## Still required before production

- Verify the current bKash sandbox and production URLs supplied for the merchant account.
- Add Refresh Token handling before the one-hour token lifetime expires.
- Add provider reconciliation or webhook handling for payments completed after the browser closes.
- Add query/refund operations and idempotency tests for the merchant account.
- Configure production credentials only in Render's private environment settings.

## Next checkpoint

After the sandbox flow works, we will harden callback/reconciliation behavior
and run the full production simulation.
