# Django Ecommerce 41: Fake Payment Status

This lesson adds a safe payment-state simulation without connecting to a
payment provider.

## Goal

Represent the difference between an order's fulfillment status and its
payment status.

## What We Built

- `payment_status` on `Order`
- Pending, paid, and failed payment choices
- Protected demo payment endpoint
- Success-page payment status display
- Demo button that marks the current order as paid
- Admin payment-status column and filter
- Migration `0004_order_payment_status`
- Regression test for the fake payment flow

## Two Separate States

```text
Order status       -> Pending / Paid / Cancelled
Payment status     -> Pending / Paid / Failed
```

The demo action changes only `payment_status`. The order can be paid while
still being pending fulfillment, which is a useful distinction for a real
commerce system.

## Safety Boundary

This is intentionally fake. It does not collect card data, call a payment
provider, verify a transaction, or claim that money moved. It only teaches
how a payment result can change a database record behind a protected POST
action.

## Flow

```text
Place pending order
  -> Success page shows payment pending
  -> POST demo payment action
  -> Save payment_status = paid
  -> Return to success page
```

The action only works for the order stored in the current session, so another
visitor cannot mark an arbitrary order as paid through this demo route.

## Main Files

```text
shop/models.py
shop/views.py
shop/urls.py
shop/admin.py
shop/templates/shop/order_success.html
shop/migrations/0004_order_payment_status.py
shop/tests.py
```

## Run And Verify

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py runserver 8001
```

Manual checklist:

1. Add a product and complete checkout.
2. Confirm the success page shows payment as pending.
3. Click **Simulate successful payment**.
4. Confirm payment changes to paid while order status remains pending.
5. Open admin and inspect both status fields.

## Checkpoint

You understand:

- why payment status deserves its own field
- why a fake payment flow must be clearly labeled
- why state-changing actions use POST
- why the current-order session check matters
- why paid does not necessarily mean fulfilled

## Next Lesson

Lesson 42 will add receipt email behavior using the project’s existing email
lessons as a safe foundation.
