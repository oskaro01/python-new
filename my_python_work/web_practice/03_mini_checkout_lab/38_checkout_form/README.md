# Django Ecommerce 38: Checkout Form

This lesson adds customer details and an order review screen. It still does
not create an `Order` row or process payment.

## Goal

Collect valid customer information while keeping the cart total under server
control.

## What We Built

- Checkout page
- Customer name field
- Email validation
- Optional phone field
- Optional order notes
- Empty-cart protection
- Server-side total recalculation
- Review page
- Form validation tests

## Checkout Flow

```text
Cart
  -> GET /checkout/
  -> customer form
  -> POST /checkout/review/
  -> validated review page
```

The review page is the end of this lesson. It does not create an order,
deduct stock, charge a card, or send an email.

## Important Security Boundary

The browser submits customer details, but it does not submit a trusted total.
The server:

1. loads the current session cart
2. loads current active products
3. limits quantities to current stock
4. calculates line totals from database prices
5. validates customer details with `CheckoutForm`
6. renders the review

This matters because hidden HTML fields and browser requests can be changed by
the user.

## Main Files

```text
shop/forms.py
shop/views.py
shop/cart.py
shop/urls.py
shop/templates/shop/checkout.html
shop/templates/shop/checkout_review.html
shop/tests.py
```

## Routes

```text
GET  /checkout/
POST /checkout/review/
```

## Run And Verify

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py runserver 8001
```

Open:

```text
http://127.0.0.1:8001/cart/
http://127.0.0.1:8001/checkout/
```

Manual checklist:

1. Add a product to the cart.
2. Open Checkout.
3. Submit an invalid email and observe the form error.
4. Submit valid customer details.
5. Confirm the review page shows the current item and total.
6. Confirm no order has been created yet.

## Checkpoint

You understand:

- how a Django form validates customer input
- why an empty cart cannot start checkout
- why the server recalculates totals
- why checkout details and an order are different concepts
- why payment success must not be claimed yet

## Next Lesson

Lesson 39 will introduce `Order` and `OrderItem` database models.
