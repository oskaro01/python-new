# Mini Checkout Lab

This is a separate ecommerce learning project. It does not modify the
Personal Dictionary app.

## Lesson Order

1. [Lesson 36: Product Catalog](36_product_catalog/README.md)
2. [Lesson 37: Session Cart](37_session_cart/README.md)
3. [Lesson 38: Checkout Form](38_checkout_form/README.md)
4. [Lesson 39: Orders and Order Items](39_orders_and_items/README.md)
5. [Lesson 40: Shipping and Contact Details](40_shipping_contact_details/README.md)
6. [Lesson 41: Fake Payment Status](41_fake_payment_status/README.md)
7. [Lesson 42: Receipt Email](42_receipt_email/README.md)
8. [Lesson 43: Tests, Security, and Deployment](43_tests_security_deployment/README.md)
9. [Lesson 44: Postgres and Resend Deployment](44_postgres_resend_deployment/README.md)
10. [Lesson 45: Product Types and Inventory](45_product_types_inventory/README.md)
11. [Lesson 46: Shipping Methods and Costs](46_shipping_methods_costs/README.md)
12. [Lesson 47: Real Payment Sandbox](47_real_payment_sandbox/README.md)
13. Planned: Payment Callbacks and Verification
14. Planned: Physical Fulfillment and Tracking
15. Planned: Secure Digital Fulfillment
16. Planned: Order History and Customer Purchases

Each lesson has its own README so we can study, verify, and commit one
checkpoint at a time.

## Project Files

```text
03_mini_checkout_lab/
    manage.py
    mini_checkout_lab/
        settings.py
        urls.py
        asgi.py
        wsgi.py
    shop/
        models.py
        views.py
        cart.py
        forms.py
        migrations/
        admin.py
        tests.py
```

## Run The Current Project

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py runserver 8001
```

Open:

```text
http://127.0.0.1:8001/
http://127.0.0.1:8001/cart/
http://127.0.0.1:8001/admin/
```

The ecommerce lab has its own `db.sqlite3`, settings, migrations, and admin
site. It does not use the Personal Dictionary database.

## Not Built Yet

The lab currently has demo payment status and receipt email delivery. Real
payment processing, shipping integrations, fulfillment workflows, and customer
purchase history are planned as separate lessons. The final design will support
physical, digital, and hybrid products rather than only digital downloads.
