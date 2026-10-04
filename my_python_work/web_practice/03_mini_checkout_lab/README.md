# Mini Checkout Lab

This is a separate ecommerce learning project. It does not modify the
Personal Dictionary app.

We are building it in small checkpoints:

1. Product catalog
2. Session cart
3. Checkout form
4. Order and order-item models
5. Shipping/contact details
6. Fake payment status
7. Receipt email
8. Tests, security, and deployment decisions

Lesson 36 intentionally stopped before carts and payments. A product was only
a catalog record at that stage.

## Lesson 36: Product Catalog

The first lesson teaches:

- creating a separate Django project
- modeling product data
- storing money with `DecimalField`, not floating-point numbers
- using a slug for readable detail URLs
- hiding inactive products from the public catalog
- managing products in Django Admin
- writing a small catalog test

The current model is:

```text
Product
  name
  slug
  description
  price
  stock
  is_active
  created_at
  updated_at
```

## Run It

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py runserver 8001
```

Open:

```text
http://127.0.0.1:8000/
```

Create an admin account when needed:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py createsuperuser
```

Then open:

```text
http://127.0.0.1:8000/admin/
```

Create a few products there. Active products appear on the public catalog;
inactive products remain stored but are hidden from customers.

## Lesson 37: Session Cart

The second lesson teaches:

- storing a temporary cart in Django's session
- keeping product truth in the database
- adding, updating, and removing cart items
- calculating line totals from database prices
- limiting quantities to current stock
- rejecting inactive products
- testing cart behavior without creating an order

The session contains only small temporary data:

```text
{
  "cart": {
    "product_id": quantity
  }
}
```

The cart does not store the price. When the cart is displayed, the server
loads the current `Product` rows and calculates totals from those prices.

Run the current checkpoint:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
```

Open:

```text
http://127.0.0.1:8001/
http://127.0.0.1:8001/cart/
```

Add a product, change its quantity, remove it, and then mark the product
inactive in Admin. The cart will no longer treat an inactive product as
available.

## What We Are Not Building Yet

There is no cart, checkout, payment provider, shipping form, or customer
account in this checkpoint. Those are separate concepts and will arrive one
at a time.
