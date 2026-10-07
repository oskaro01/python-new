# Django Ecommerce 53: Customer Accounts And Order History

This lesson adds the customer side of post-purchase access.

## What We Built

- Customer registration and login using Django auth
- Authenticated checkout orders linked to the signed-in customer
- A protected `My orders` page
- Owners can reopen their own order pages after the original checkout session
  expires
- Guest checkout still works exactly as before
- Guest orders remain inaccessible through the account history page
- Existing guest orders remain guest orders; we do not guess their ownership

## Order Access Rules

```text
Guest checkout
  -> order visible through the current checkout session

Signed-in checkout
  -> order linked to the user
  -> order appears in My orders
  -> owner can reopen the order page later
```

Digital download links remain independently protected by their signed,
expiring token. Having an account does not bypass payment verification.

## Practice Checkpoint

1. Visit `/register/` and create a customer account.
2. Add a product and complete checkout while logged in.
3. Visit `/orders/` and confirm the order appears.
4. Log out and confirm `/orders/` requires login.
5. Log in as a different user and confirm the order is not visible.

## Next Pending Integrations

- Pathao location IDs and webhook integration remain pending while the sandbox
  endpoint returns HTTP `522`.
- bKash sandbox payment and webhooks remain pending.
- Refunds are still planned.

## Next Lesson

Lesson 54 will cover refunds, cancellations, and how payment, inventory, and
fulfillment states are reversed safely.
