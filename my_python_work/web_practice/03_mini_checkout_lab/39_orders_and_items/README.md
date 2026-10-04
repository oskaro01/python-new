# Django Ecommerce 39: Orders And Order Items

This lesson turns a reviewed cart into a real pending order.

## Goal

Persist the checkout result in the database while preserving the exact
product information used at the time of ordering.

## What We Built

- `Order` model
- `OrderItem` model
- Pending order status
- Place-order confirmation action
- Order success page
- Order Admin view with item inline rows
- Historical product name and price snapshots
- Cart clearing after successful order creation
- Transactional order creation
- Session-protected order success page

## Database Structure

```text
Order
  full_name
  email
  phone
  notes
  status
  total_amount
  created_at
  updated_at

OrderItem
  order
  product
  product_name
  unit_price
  quantity
  line_total
```

One order has many order items:

```text
Order 1 ─────── many OrderItem rows
```

## Why Order Items Store Snapshots

Products can change later. A product name or price in the catalog is not
necessarily the name or price used for an old order.

When the order is created, each item copies:

```text
product.name  -> product_name
product.price -> unit_price
```

The old order remains historically accurate even if the product changes or is
deleted later.

## Order Flow

```text
Cart
  -> Checkout form
  -> Review
  -> POST Place order
  -> Order + OrderItem rows
  -> Clear cart
  -> Success page
```

Order creation uses a database transaction so the order and its items are
created together.

This lesson does not deduct stock or process payment yet. The order starts as
`pending`; those concerns arrive in later lessons.

## Main Files

```text
shop/models.py
shop/admin.py
shop/views.py
shop/urls.py
shop/templates/shop/checkout_review.html
shop/templates/shop/order_success.html
shop/migrations/0002_order_orderitem.py
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

1. Add a product to the cart.
2. Complete Checkout.
3. Click **Place order** on the review page.
4. Confirm the cart is empty afterward.
5. Open `/admin/` and inspect the order and item snapshot.
6. Change the product price and confirm the old order still shows its old price.

## Checkpoint

You understand:

- why a cart is temporary but an order is permanent
- why an order needs separate item rows
- why historical prices must be snapshotted
- why order creation belongs inside a transaction
- why a pending order is not the same as a paid order

## Next Lesson

Lesson 40 adds shipping and contact details as explicit order data.
