# Django Ecommerce 46: Shipping Methods And Costs

This lesson adds server-owned shipping choices to the checkout total.

## Goal

Let customers choose a delivery method for physical orders while keeping
digital-only orders free from unnecessary shipping fields and charges.

## What We Built

- Standard and express shipping methods
- Fixed server-side rates for each method
- Shipping method selection in checkout
- Shipping method and amount stored on `Order`
- Shipping included in the order total
- Shipping details shown in review, success, and receipt emails
- Digital-only carts skip shipping selection and cost
- Physical and hybrid carts require a shipping method

## Current Rates

```text
Standard delivery: $5.00
Express delivery:  $12.00
```

These are learning-lab rates. A later production version can replace the
static table with a courier or carrier-rate service without changing the
checkout contract.

The browser submits only a method key. The server looks up the amount, so a
customer cannot change the shipping price by editing the HTML form.

## Order Structure

```text
Order
  shipping_method
  shipping_amount
  total_amount = item subtotal + shipping amount
```

Stock is still not deducted at order creation. Inventory changes belong after
verified payment in a later lesson.

## Run And Verify

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
```

Manual checklist:

1. Add a physical product to the cart.
2. Choose Standard delivery and confirm the total increases by `$5.00`.
3. Repeat with Express delivery and confirm the total increases by `$12.00`.
4. Add only a digital product and confirm shipping is not required.
5. Open the order in Admin and inspect the saved method and amount.

## Checkpoint

You understand:

- why shipping rates must be resolved on the server
- why the shipping amount belongs on the permanent order
- how product type controls whether shipping is required
- why checkout totals must include shipping before payment begins

## Next Lesson

Lesson 47 connects the checkout to a real payment sandbox.
