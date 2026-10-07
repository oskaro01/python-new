# Django Ecommerce 54: Refunds And Cancellations

This lesson adds the reverse side of checkout: safely cancelling an order,
refunding a paid payment, and restoring inventory exactly once.

## State Transitions

```text
Pending order
  -> Cancelled

Paid + processing order
  -> provider refund
  -> inventory restored
  -> Cancelled

Shipment already created
  -> cannot cancel directly
  -> use a future return workflow
```

The general order state, payment state, inventory state, and fulfillment state
remain separate. A cancelled paid order can therefore show:

```text
Order: Cancelled
Payment: Refunded
Inventory: Restored
Fulfillment: Ready for fulfillment
```

## What We Built

- `refunded` payment status with provider refund references
- Inventory restoration with row locks
- Idempotent cancellation so stock is not restored twice
- Demo refunds for local learning
- Stripe refund calls with a stable idempotency key
- Customer cancellation while an order has not been shipped
- Admin action for cancellation/refund review
- Rejection of direct cancellation after a shipment exists

## Important Real-World Rule

Once a courier consignment exists, cancellation becomes a courier operation.
The customer may need a return, refusal, or reverse-pickup workflow. We do not
pretend that changing our local order status cancels a parcel already held by a
carrier.

## Practice Checkpoint

1. Create a physical product with stock `2`.
2. Place and complete a demo-paid order.
3. Cancel it before creating a shipment.
4. Confirm payment becomes `Refunded` and stock returns to `2`.
5. Repeat the cancellation request and confirm stock does not increase again.
6. Create a shipment for another paid order and confirm cancellation is
   rejected.

## Pending Integrations

- Pathao location IDs and webhook integration remain pending while its sandbox
  returns HTTP `522`.
- bKash sandbox payment and webhook integration remain pending.

## Next Lesson

Lesson 55 will cover returns and reverse logistics after a courier shipment.
