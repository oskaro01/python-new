# Lesson 55: Returns and Reverse Logistics

This lesson adds the workflow that starts after a delivered physical order
needs to come back to the seller.

## Lifecycle

```text
Delivered order
  -> Requested
  -> Approved or rejected
  -> Return in transit
  -> Received for inspection
  -> Refunded
```

The customer only creates a return request. Staff review it and control the
physical reverse-shipping steps. Receiving an item does not automatically
refund it; the final refund/restock action is explicit.

## What Is Recorded

`ReturnRequest` stores:

- the related order
- the customer's reason
- the current return status
- staff review notes
- pickup provider and reference
- return tracking number
- request, review, received, and completion timestamps

The first provider is `manual`, with a predictable demo reference. Later this
boundary can call a courier's reverse-shipment API.

## Eligibility Rules

A return can be requested only when:

- the customer owns the order and is signed in
- payment is confirmed
- the order has a physical or hybrid item
- the order shipment is delivered
- no previous return request exists

Completed digital-only orders do not enter this physical return workflow.

## Refund and Inventory Safety

The final transition:

1. Refunds the original payment through the demo provider or Stripe.
2. Restores deducted physical inventory once.
3. Marks the order as `Returned`.
4. Marks payment as `Refunded`.
5. Marks fulfillment as `Returned`.
6. Marks the return request as `Refunded`.

The transition is idempotent. Repeating it does not create a second refund or
increase stock twice. In a later async lesson, this provider call will move to
a background job so a slow courier or payment provider cannot hold up an admin
request.

## Local Walkthrough

1. Create and pay a physical order.
2. In Admin, create a sandbox shipment for the paid order.
3. Change the shipment status to `Delivered`.
4. Sign in as the order's customer and open the order page.
5. Submit a return request with a reason.
6. In Admin -> Return requests, approve it.
7. Mark it `in transit`, then `received`.
8. Use `Refund and restock selected received returns`.
9. Reopen the order and verify the returned/refunded state and restored stock.

## Next Lesson

Lesson 56 will move slow work such as receipts, refunds, courier calls, and
webhook processing into background jobs with retries and visible job status.
