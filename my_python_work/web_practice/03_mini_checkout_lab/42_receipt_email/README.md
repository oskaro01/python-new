# Django Ecommerce 42: Receipt Email

This lesson sends one order receipt after the demo payment becomes paid.

## Goal

Build a receipt-email boundary that works locally for free, is testable without
the internet, and does not send duplicate receipts.

## What We Built

- `shop/emails.py` email service
- Plain-text order receipt template
- Console email backend as the local default
- Configurable backend and sender environment variables
- `receipt_sent_at` timestamp on `Order`
- Migration `0005_order_receipt_sent_at`
- Receipt status on the order success page and in admin
- In-memory email tests for recipient, subject, items, and one-send behavior

## Receipt Flow

```text
Payment changes from pending to paid
  -> Render receipt template
  -> Send receipt
  -> Save receipt_sent_at
  -> Do not send again for repeated requests
```

Payment and email are separate outcomes. If email delivery fails, the payment
remains paid and the customer sees a receipt error message.

## Local Email Backend

The lab defaults to Django's console backend:

```text
django.core.mail.backends.console.EmailBackend
```

That prints the complete receipt in the terminal instead of sending it over
the internet. It is free and safe for learning.

The settings can later be changed through environment variables:

```text
DJANGO_EMAIL_BACKEND
DEFAULT_FROM_EMAIL
```

## Main Files

```text
mini_checkout_lab/settings.py
shop/emails.py
shop/models.py
shop/views.py
shop/admin.py
shop/templates/shop/emails/order_receipt.txt
shop/templates/shop/order_success.html
shop/migrations/0005_order_receipt_sent_at.py
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

1. Complete checkout and place an order.
2. Click **Simulate successful payment**.
3. Check the terminal for the receipt email.
4. Confirm the success page says the receipt was sent.
5. Refresh or repeat the payment request and confirm no second receipt is sent.

## Checkpoint

You understand:

- why email code belongs in a separate service
- why local development should use a safe backend
- why payment success and receipt delivery are separate outcomes
- how a timestamp prevents duplicate email
- how Django tests email without contacting a provider

## Next Lesson

Lesson 43 finishes the checkout lab with broader tests, security checks, and
deployment preparation.
