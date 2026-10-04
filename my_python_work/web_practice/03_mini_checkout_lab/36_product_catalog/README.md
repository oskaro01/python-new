# Django Ecommerce 36: Product Catalog

This is the first lesson in the separate Mini Checkout Lab.

## Goal

Build a small public catalog managed through Django Admin.

## What We Built

- A separate Django project
- A `Product` model
- Admin product management
- Public product list and detail pages
- Product slugs for readable URLs
- Active/inactive catalog visibility
- Stock display
- Basic catalog tests

The model is:

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

## Important Ideas

### Money uses `DecimalField`

Product prices use:

```python
price = models.DecimalField(max_digits=10, decimal_places=2)
```

Money should not use ordinary floating-point values because small rounding
errors can become business errors.

### The slug is for the URL

A product named `Canvas Tote` can have this URL:

```text
/products/canvas-tote/
```

The numeric database ID still identifies the row internally.

### Active is different from stored

An inactive product remains in the database for admin history, but the public
catalog does not show it.

## Main Files

```text
shop/models.py
shop/admin.py
shop/views.py
shop/urls.py
shop/templates/shop/product_list.html
shop/templates/shop/product_detail.html
shop/tests.py
shop/migrations/0001_initial.py
```

## Run And Verify

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py runserver 8001
```

Create an admin account:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py createsuperuser
```

Open:

```text
http://127.0.0.1:8001/admin/
```

Create these practice products:

```text
Canvas Tote       12.50   stock 10   active
Notebook           6.99   stock 25   active
Hidden Test Item  20.00   stock 5    inactive
```

Then open:

```text
http://127.0.0.1:8001/
```

The two active products should appear. The inactive product should stay
hidden.

## Checkpoint

You understand:

- how a product becomes a database row
- how Admin manages catalog data
- why price uses `DecimalField`
- why a stored product can be hidden from customers
- how a slug connects a readable URL to one product

## Next Lesson

[Lesson 37: Session Cart](../37_session_cart/README.md)
