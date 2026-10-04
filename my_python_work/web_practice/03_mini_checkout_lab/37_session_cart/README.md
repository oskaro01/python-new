# Django Ecommerce 37: Session Cart

This lesson adds a temporary shopping cart without creating order records yet.

## Goal

Let a visitor add products, change quantities, remove items, and see a total.

## What We Built

- Add to cart
- Update quantity
- Remove item
- Cart item count in navigation
- Cart total
- Session-based storage
- Stock-limit validation
- Inactive-product protection
- Messages after cart actions
- Cart tests

## Where The Data Lives

The cart is stored in the visitor's Django session:

```text
{
  "cart": {
    "product_id": quantity
  }
}
```

For example:

```text
{
  "cart": {
    "3": 2,
    "7": 1
  }
}
```

The session stores only product IDs and quantities. It does not store the
price.

## Source Of Truth

The database remains authoritative:

```text
Database:
  product name
  price
  stock
  active status

Session:
  product ID
  requested quantity
```

When the cart is displayed, Django loads current product rows and calculates
line totals from the database price. The browser cannot set its own price.

## Main Files

```text
shop/cart.py
shop/context_processors.py
shop/views.py
shop/urls.py
shop/templates/shop/cart_detail.html
shop/templates/shop/base.html
shop/tests.py
```

## Cart Routes

```text
GET  /cart/
POST /cart/add/<product_id>/
POST /cart/update/<product_id>/
POST /cart/remove/<product_id>/
```

Cart-changing actions use `POST` and CSRF protection.

## Run And Verify

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py runserver 8001
```

Open:

```text
http://127.0.0.1:8001/
http://127.0.0.1:8001/cart/
```

Manual checklist:

1. Add an active product.
2. Open the cart and confirm the line total.
3. Increase the quantity above stock.
4. Confirm Django limits it to available stock.
5. Remove the item.
6. Mark a product inactive in Admin.
7. Confirm it cannot be added as an available product.

## Tests

The lesson currently has eight tests covering:

- active catalog visibility
- product details
- inactive product 404 behavior
- session cart storage
- stock limits
- inactive-product rejection
- cart removal
- line totals

## Checkpoint

You understand:

- why a cart can be temporary session data
- why a cart is not the same thing as an order
- why the database, not the browser, owns price and stock truth
- why cart mutations use `POST`
- why inactive products must be checked on the server

## Next Lesson

Lesson 38 will add a checkout form. It will collect customer information but
will not claim that a payment succeeded.
