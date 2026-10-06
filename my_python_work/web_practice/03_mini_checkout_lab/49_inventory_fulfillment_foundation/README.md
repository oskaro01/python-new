# Django Ecommerce 49: Inventory And Fulfillment Foundation

This lesson fixes inventory accounting and prepares paid physical orders for
the courier workflow.

## The Bug We Fixed

Before this lesson, the cart checked stock when adding an item, but payment
never reduced `Product.stock`. A product that started with three units could
therefore be purchased repeatedly forever.

## New Rule

Physical and hybrid stock is deducted only after verified payment:

```text
payment confirmed
  -> lock product rows
  -> check every requested quantity
  -> deduct stock once
  -> record inventory_deducted_at
```

Digital products do not use physical stock. If a repeated webhook arrives,
the recorded inventory status prevents a second deduction.

## Inventory States

```text
not_required
pending
deducted
unavailable
```

If payment succeeds after stock has become unavailable, the order is marked
`unavailable` for manual review or refund handling. The system never deducts
negative stock.

## Checkpoint

Create a physical product with stock `3`, complete three paid orders, and
confirm the fourth order cannot be added after stock reaches `0`.

## Next Lesson

Lesson 50 connects paid physical orders to a courier API, creates consignments,
and stores tracking updates.
