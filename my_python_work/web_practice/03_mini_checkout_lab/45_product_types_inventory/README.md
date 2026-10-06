# Django Ecommerce 45: Product Types And Inventory

This lesson makes the catalog explicit about what kind of product it sells.

## Goal

Support physical, digital, and hybrid products without treating digital
downloads as if they require physical stock or shipping.

## What We Built

- `Product.product_type` choices: Physical, Digital, or Physical + digital
- Inventory rules for physical and hybrid products
- Digital products remain purchasable when physical stock is zero
- A maximum session quantity for digital products
- Product type shown in the catalog and cart
- Product type copied into each `OrderItem` as a historical snapshot
- Shipping fields become optional for digital-only carts
- Physical and hybrid carts still require shipping details
- Product type and inventory visibility in Django Admin

## Product Rules

```text
Physical
  stock controls availability
  shipping is required

Digital
  stock is not used for availability
  shipping is optional
  quantity is capped per cart session

Physical + digital
  stock controls availability
  shipping is required
```

The current lesson does not deduct stock when an order is created. An order
can be abandoned or payment can fail, so inventory deduction belongs after
verified payment in a later lesson.

## Database Changes

```text
Product
  product_type

OrderItem
  product_type
```

The `OrderItem` snapshot protects historical order meaning if the product's
type changes later in Admin.

## Run And Verify

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
```

In Admin, create one product of each type. Give the digital product stock
zero and confirm it can still be added to the cart. Give a physical product
stock zero and confirm it cannot be added.

## Checkpoint

You understand:

- why product type is domain data, not only presentation text
- why digital availability should not depend on physical stock
- why an order item stores the product type snapshot
- why shipping requirements depend on the cart contents
- why stock should be deducted after verified payment rather than order draft creation

## Next Lesson

Lesson 46 adds shipping methods and calculates shipping costs.
