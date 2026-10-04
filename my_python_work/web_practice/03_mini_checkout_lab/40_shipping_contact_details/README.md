# Django Ecommerce 40: Shipping And Contact Details

This lesson makes delivery information part of the permanent order record.

## Goal

Collect a customer's shipping address during checkout and preserve it on the
`Order` row when the order is placed.

## What We Built

- Required shipping address, city, postal code, and country fields
- Shipping fields in `CheckoutForm`
- Shipping details on the review page
- Shipping details saved during transactional order creation
- Shipping details on the order success page
- Admin search support for shipping city and postal code
- Migration `0003_order_shipping_address_order_shipping_city_and_more`

## Order Structure

```text
Order
  full_name
  email
  phone
  shipping_address
  shipping_city
  shipping_postal_code
  shipping_country
  notes
  status
  total_amount
```

The checkout form is temporary session data. The order is the permanent
record, so the shipping values are copied into the database during placement.

## Flow

```text
Checkout form
  -> Validate contact and shipping data
  -> Review shipping details
  -> Place pending order
  -> Save shipping data on Order
```

This lesson still does not process payment or connect to a shipping provider.
It only gives the order a reliable destination record.

## Main Files

```text
shop/forms.py
shop/models.py
shop/views.py
shop/admin.py
shop/templates/shop/checkout.html
shop/templates/shop/checkout_review.html
shop/templates/shop/order_success.html
shop/migrations/0003_order_shipping_address_order_shipping_city_and_more.py
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

1. Add a product and open checkout.
2. Fill in the contact and shipping fields.
3. Confirm the shipping details appear on the review screen.
4. Place the order.
5. Confirm the success screen and admin order include the same address.

## Checkpoint

You understand:

- why shipping data belongs on the permanent order
- how a form's cleaned data becomes model data
- why migrations are required when the model changes
- how admin search can support order operations
- why shipping data does not mean shipping has been integrated

## Next Lesson

Lesson 41 will add a fake payment status flow without connecting to a real
payment provider.
