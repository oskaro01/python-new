# Mini Checkout Lab: Customer Accounts and Order History

The checkout supports both guests and registered customers. The important
design choice is to preserve that distinction instead of guessing who owns an
old guest order.

## Two order access paths

```text
Guest checkout
  -> Order.customer = NULL
  -> last_order_id session access

Signed-in checkout
  -> Order.customer = request.user
  -> My orders query later
  -> owner can reopen the order page
```

The order itself is durable database data. The session is only one temporary
way to authorize the success page immediately after checkout.

## 1. Registration

The customer opens:

```text
GET /register/
```

The shop view creates `RegisterForm`, which is based on Django's
`UserCreationForm` and adds a required email field. The template includes a
CSRF-protected POST form.

The POST flow is:

```text
POST /register/
  -> username/password/email validation
  -> password hashing by UserCreationForm
  -> INSERT auth_user
  -> login(request, user)
  -> session stores authenticated user ID
  -> redirect to product list
```

The password is never stored as plaintext. The new account is immediately
logged in, so the next checkout request has an authenticated `request.user`.

If an already authenticated user opens registration, the view redirects to
order history instead of creating another account through that page.

## 2. Checkout links the customer

At `place_order`, the checkout code creates the order with:

```python
customer=request.user if request.user.is_authenticated else None
```

The same checkout form works for both cases. The only difference is whether the
foreign key is populated.

```text
anonymous request -> customer_id = NULL
authenticated request -> customer_id = current user's ID
```

The order also snapshots the customer's name, email, phone, and address. Those
values remain useful even if the user later changes their account profile.

## 3. Immediate order-success access

After order creation, the view stores:

```text
last_order_id = newly created order ID
```

The success page authorizes access with either:

```text
session last_order_id matches order ID
OR
authenticated user owns the order
```

This lets a guest see the order they just created without exposing every order
number as a public lookup. It also lets a signed-in customer reopen their own
order later.

If neither condition is true, the view returns 404. Knowing another person's
numeric order ID is not enough.

## 4. My orders page

The customer opens:

```text
GET /orders/
```

The view has `@login_required`, so a guest is redirected to login. For an
authenticated customer, the query is:

```python
Order.objects.filter(customer=request.user).prefetch_related(
    "items", "shipment"
)
```

The database filter is the privacy boundary. It does not fetch all orders and
filter them in a template; it asks the database for only this user's orders.

The page displays each order's:

```text
order number
creation date
business status
payment status
fulfillment status
```

Each row links back to the protected order-success view.

Guest orders do not appear in `My orders` because they have no customer foreign
key. Existing guest orders are not automatically attached to a new account
based on matching email; that would be an unsafe ownership guess.

## 5. Returning to a digital order

The order-success view rebuilds download links when:

```text
order is paid
item is digital or hybrid
item has a stored digital filename
```

The account relationship does not itself grant file access. Each link still
contains a signed, expiring token tied to the exact order and item.

Therefore:

```text
account ownership -> may reopen the order page
paid order + valid token -> may download the purchased file
```

An authenticated user cannot download an unpaid item merely because it appears
in their order history.

## 6. Logout and account separation

The navigation bar submits a CSRF-protected POST to Django's logout view. The
session authentication identity is cleared. The cart session may continue to
exist, but protected order history no longer loads because `request.user` is
anonymous.

After another user logs in, the same browser session now produces a different
`request.user`. The order-history query therefore returns a different set of
orders.

## Order ownership sequence

```text
register
  -> auth_user row + authenticated session
  -> add products and checkout
  -> place_order reads request.user
  -> Order.customer_id = that user's ID
  -> last_order_id allows immediate success page
  -> GET /orders/ filters by customer=request.user
  -> order link rechecks ownership
  -> paid digital item gets signed download URL
```

## Security boundaries

- Passwords are hashed by Django's user form.
- Registration and logout use CSRF-protected POST forms.
- Anonymous orders are not placed into an account by email guessing.
- `My orders` requires login and filters by the current user in SQL.
- Order-success access requires the current checkout session or ownership.
- Return requests require the authenticated order owner.
- Digital downloads require payment and a signed, expiring item token.

## Debugging checklist

```text
order missing from history -> checkout happened while logged out
guest sees another order   -> success authorization is wrong
history shows all orders   -> customer=request.user filter is missing
user can download unpaid   -> payment/token checks are missing
login loses order access   -> session or customer foreign key is wrong
old guest order appears    -> unsafe email-based ownership merge
registration stores secret  -> password hashing flow was bypassed
```

## Files involved

- `shop/forms.py`: customer registration form.
- `shop/views.py`: registration, checkout ownership, success access, and history.
- `shop/urls.py`: account and order-history routes.
- `shop/models.py`: `Order.customer` relationship.
- `shop/templates/registration/register.html`: registration form.
- `shop/templates/registration/login.html`: login form.
- `shop/templates/shop/base.html`: account navigation and logout.
- `shop/templates/shop/order_history.html`: customer order list.
- `shop/downloads.py`: signed digital-download access.
