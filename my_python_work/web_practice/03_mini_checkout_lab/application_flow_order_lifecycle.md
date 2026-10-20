# Mini Checkout Lab: End-to-End Order Lifecycle

This document follows a customer from the product catalog to a saved pending
order. It deliberately stops before payment. A payment provider is a later
event attached to this order; it should not be mixed into the cart and order
creation foundation.

## The application map

```text
Browser
  -> shop URL
  -> Django view
  -> Product database or session cart
  -> checkout form validation
  -> transaction.atomic()
  -> Order + OrderItem rows
  -> clear checkout session data
  -> order-success page
  -> payment may begin afterward
```

The cart is temporary browser-session state. The order is durable database
state. The cart does not become an order until the customer presses Place
order and Django writes both the order and its item snapshots.

## 1. Catalog request

The customer opens:

```text
GET /
```

`mini_checkout_lab/urls.py` delegates the root path to `shop/urls.py`. The
`product_list` view queries:

```python
Product.objects.filter(is_active=True)
```

The database is the source of current product names, prices, product types,
and stock. The template displays active products and forms that submit to the
cart routes.

Opening a product detail page uses:

```text
GET /products/<slug>/
```

The view requires both the matching slug and `is_active=True`. An inactive or
unknown product is not presented as purchasable.

## 2. Adding a product to the cart

The product form submits:

```text
POST /cart/add/<product_id>/
```

The view loads the active product from the database and checks
`product.is_available`. A physical or hybrid product needs stock; a digital
product does not require physical inventory.

The cart stores only a small dictionary in the session:

```python
{
    "12": 2,
    "19": 1,
}
```

The keys are product IDs and the values are quantities. It does not store the
price or product name. That is intentional: prices and availability must be
read again from the database instead of trusting values sent by the browser.

`add_product()` limits the quantity to stock for inventory-tracked products or
to the digital maximum of 99. `save_cart()` writes the dictionary to the
session and marks the session modified.

The response can be either:

```text
normal form -> success message + redirect
AJAX request -> JSON {ok, message, cart_count}
```

No `Order` row exists yet.

## 3. Rendering the cart

The customer opens:

```text
GET /cart/
```

`get_cart_items()` reads the session dictionary, then queries active products
whose IDs are in the cart. It rehydrates each session entry with current
database data:

```text
session product ID + quantity
  -> Product row
  -> current price
  -> current stock
  -> line_total = price * quantity
```

If a product was deactivated, deleted, or became out of stock, it is removed
from the cleaned session cart. Quantities are also limited again to current
stock. This protects the cart from becoming a stale promise about inventory.

`get_cart_total()` sums Decimal line totals. It does not use floating-point
money arithmetic.

The cart page displays each product, quantity, current line total, and the
checkout link. Update and remove are separate POST actions protected by CSRF.

## 4. Updating or removing cart entries

Updating submits:

```text
POST /cart/update/<product_id>/
quantity=3
```

The view converts the quantity to an integer. Invalid input produces a
message. Valid input goes through `update_product()`, which applies the same
stock or digital-quantity limit before saving the session.

Removing submits:

```text
POST /cart/remove/<product_id>/
```

`remove_product()` deletes only that session key. Neither action creates or
changes an order.

## 5. Starting checkout

The customer opens:

```text
GET /checkout/
```

The view rebuilds the cart first. An empty cart is redirected back to the cart
page with an informational message.

The product types determine whether shipping is needed:

```text
physical or hybrid -> shipping required
digital only       -> shipping fields optional and no shipping method
```

`CheckoutForm` receives `requires_shipping` and configures its fields and
shipping-method choices accordingly. The checkout page shows the current
items and subtotal.

## 6. Reviewing customer details

The form submits:

```text
POST /checkout/review/
```

The view rebuilds the cart again, constructs `CheckoutForm(request.POST, ...)`,
and validates name, email, address fields, and shipping method.

If invalid, the same checkout template is rendered with status 400 and field
errors. No order is created.

If valid, the cleaned customer data is stored temporarily in the session under
`checkout_customer`. The view then reloads the cart from the database one more
time before calculating the review totals. Shipping cost is calculated by the
server through `shipping_cost()`, never accepted as a browser-submitted price.

The review page displays:

```text
customer details + item snapshots + subtotal + shipping + total
```

At this point the database still has no new order. The session contains the
customer form data, while the cart session contains product IDs and quantities.

## 7. Placing the order

The customer confirms through:

```text
POST /checkout/place-order/
```

The view performs its own safety checks instead of trusting the review page:

1. Rebuild the cart.
2. Reject an empty cart.
3. Read `checkout_customer` from the session.
4. Revalidate it with `CheckoutForm`.
5. Recalculate the cart total from current Product rows.
6. Recalculate shipping on the server.

The total sent to the database is therefore:

```text
current product prices * current quantities + server shipping cost
```

The browser cannot change the total by editing HTML or sending a hidden price
field.

## 8. The database transaction

The order and its items are created inside:

```python
with transaction.atomic():
```

The first insert creates an `Order` row containing:

- authenticated customer, if the visitor is logged in
- customer name and contact information
- shipping details and shipping amount
- total amount
- pending order status
- pending payment status
- inventory and fulfillment status defaults

The second operation bulk-creates one `OrderItem` per cart item. Each item
stores a snapshot:

```text
product foreign key
product_name
product_type
unit_price
quantity
line_total
digital_file_name
```

The foreign key helps connect the item to the current product. The copied
fields preserve what the customer ordered even if the product name or price
changes later. This is why an order should not calculate its old receipt from
the current Product row alone.

If an exception occurs inside the atomic block, Django rolls back the order
and item inserts together. It should not leave an order without its items.

## 9. Cleaning the session after success

After the transaction commits, the view removes:

```text
cart
checkout_customer
```

It stores the new ID as:

```text
last_order_id
```

Then it redirects to:

```text
GET /orders/<order_id>/success/
```

The cart is now empty because the durable Order and OrderItem rows have taken
over. The order ID in the session gives an anonymous checkout visitor a safe,
short-lived way to see the result page they just created.

## 10. Order-success authorization

The success view loads the order and decides whether the visitor may view it:

```text
session last_order_id matches order ID
OR
authenticated order.customer matches request.user
```

If neither condition is true, the view raises 404. Knowing an order number is
not sufficient by itself.

The page loads related items, shipment, return request, background jobs, and
payment state. The order is still normally:

```text
status = pending
payment_status = pending
```

The order has been created, but payment and fulfillment are separate state
transitions.

## Database shape after placing an order

```text
Product
  id, name, current price, stock, type
       │
       └── OrderItem.product

Order
  id, customer, totals, contact snapshot,
  status, payment_status, inventory_status,
  fulfillment_status
       │
       └── OrderItem.order

OrderItem
  product snapshot, quantity, line_total, digital file name
```

The session temporarily holds the cart and checkout form. The database holds
the durable commercial record.

## Complete order sequence

```text
GET /
  -> active Product rows
  -> product page

POST /cart/add/12/
  -> active/available check
  -> session {"12": quantity}
  -> redirect or JSON cart count

GET /cart/
  -> session IDs
  -> current Product rows and stock
  -> current line totals

GET /checkout/
  -> shipping requirement based on product type
  -> CheckoutForm

POST /checkout/review/
  -> validate customer fields
  -> store cleaned details in session
  -> recalculate subtotal and shipping
  -> review page

POST /checkout/place-order/
  -> rebuild cart and revalidate session data
  -> transaction.atomic()
  -> INSERT Order
  -> INSERT OrderItem rows
  -> clear cart and checkout session keys
  -> store last_order_id
  -> redirect success page
```

## Where payment fits

Payment starts after the order exists and is still pending:

```text
pending Order
  -> payment provider session/request
  -> customer completes payment externally
  -> callback/webhook or return URL
  -> verify provider response
  -> mark Order paid
  -> deduct inventory
  -> mark fulfillment readiness
  -> queue receipt
```

The payment provider does not define the product price. Django creates and
verifies the order total first, then compares provider results with the order.

## Debugging checklist

```text
cart empty unexpectedly      -> session key, product ID, active flag, stock
wrong cart total              -> Product price reload or Decimal calculation
shipping shown for digital    -> requires_shipping/product type logic
review bypasses validation    -> checkout_review must use CheckoutForm
client changes total          -> place_order must recalculate server-side
order has no items            -> transaction or bulk_create failure
refresh repeats checkout      -> POST/Redirect/GET or session cleanup issue
someone sees another order   -> success authorization or order history filter
old receipt price changes     -> missing OrderItem price snapshot
```

## Files involved

- `shop/models.py`: Product, Order, and OrderItem database records.
- `shop/cart.py`: session cart reading, limits, cleanup, and totals.
- `shop/forms.py`: checkout fields and shipping-dependent validation.
- `shop/views.py`: catalog, cart, review, order creation, and success flow.
- `shop/urls.py`: URL-to-view mapping.
- `shop/templates/shop/product_list.html`: catalog display.
- `shop/templates/shop/cart_detail.html`: session-cart actions.
- `shop/templates/shop/checkout.html`: customer form.
- `shop/templates/shop/checkout_review.html`: confirmation before order creation.
- `shop/templates/shop/order_success.html`: order state and later payment entry.
- `mini_checkout_lab/settings.py`: database, sessions, payment, and storage configuration.
