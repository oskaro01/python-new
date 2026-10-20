# Mini Checkout Lab: Cancellation, Refund, and Return Flows

Fulfillment is not finished when payment succeeds. Customers may cancel before
shipping, or request a return after delivery. These are different workflows
because the physical parcel and the payment provider are in different states.

## The decision tree

```text
order request
  |
  +-- not shipped -----------------> cancellation
  |                                    -> optional refund
  |                                    -> restore stock
  |
  +-- shipment exists -------------> direct cancellation rejected
                                       -> return workflow after delivery
                                            -> review
                                            -> reverse movement
                                            -> receive and inspect
                                            -> refund and restock
```

The application keeps order, payment, inventory, fulfillment, and return
statuses separate. One status field cannot describe all of these safely.

## 1. Customer cancellation

The order page sends:

```text
POST /orders/<order_id>/cancel/
```

The view authorizes the request with either the current session's
`last_order_id` or the authenticated order owner. It then calls
`cancel_order(order, reason)`.

Inside a transaction, the order is locked with `select_for_update()`. The
function applies the business rules in this order:

```text
already cancelled -> return unchanged
completed         -> reject cancellation
shipment exists   -> reject; use return workflow
```

An order without a shipment can still be cancelled. A pending or failed
payment needs no provider refund. A paid order must call `refund_payment()`
before it is marked refunded.

## 2. Refund provider boundary

The refund helper returns the provider reference:

```text
demo payment   -> demo-refund-order-<id>
Stripe payment -> Stripe Refund.create(...)
already refund -> existing refund reference
other provider -> configuration error
```

The Stripe request uses a stable idempotency key:

```text
order-<id>-refund
```

That protects against retrying the same refund request as a new refund. The
current implementation supports demo and Stripe refunds. bKash refund support
is not implemented in this path yet, so a bKash-paid order must not be treated
as automatically refundable.

## 3. Restoring inventory during cancellation

If the paid order already deducted physical stock, cancellation calls the
inventory restoration helper. It first checks the state:

```text
restored or not_required -> do nothing
not deducted             -> do not restore
deducted                 -> lock products and add quantities back
```

The product rows are locked while stock is restored. This prevents two
simultaneous cancellation requests from increasing stock twice.

The order then becomes:

```text
status = cancelled
payment_status = refunded   (if a refund occurred)
refund_reference = provider reference
refunded_at = server time
notes = existing notes + cancellation reason
```

Repeating cancellation returns safely without another refund or stock change.

## 4. Why shipment blocks cancellation

Once a `Shipment` row exists, the parcel may already be in a courier system.
Changing the local order to cancelled would not necessarily stop the courier.
The code therefore raises:

```text
Shipped orders must use a return workflow.
```

This is a boundary between the store database and a physical carrier. A real
carrier may support cancellation, refusal, or reverse pickup, but that must be
an explicit courier operation.

## 5. Return eligibility

The customer can request a return only when all conditions are true:

```text
authenticated owner
payment_status = paid
order.status = completed
order contains physical or hybrid item
shipment exists and shipment.status = delivered
no existing ReturnRequest
```

Digital-only orders do not enter physical reverse logistics. The order-success
page uses `order_can_be_returned()` to decide whether to show the return form.

## 6. Customer submits a return request

The customer submits:

```text
POST /orders/<order_id>/return/
```

The view requires login and loads the order with `customer=request.user`. The
`ReturnRequestForm` requires a reason. A blank reason is rejected before any
database change.

`request_order_return()` locks the order, checks eligibility again, prevents a
second request, and creates a `ReturnRequest` row:

```text
status = requested
reason = customer explanation
requested_at = server time
```

The browser only asks for the return. It cannot approve, receive, or refund
the item.

## 7. Staff controls the reverse movement

Admin actions apply guarded transitions to the return record:

```text
requested
  -> approved
  -> in_transit
  -> received
  -> refunded
```

The request can also move from `requested` to `rejected`.

Each transition locks the `ReturnRequest` row and checks its current state:

```text
approve       -> only requested
reject        -> only requested
mark transit  -> only approved
mark received -> approved or in_transit
complete      -> only received
```

Approval records staff notes, a pickup provider, a reference, and a tracking
number. The learning provider is manual and creates a predictable demo
reference such as `DEMO-RETURN-000023`.

## 8. Final return completion

The final Admin action is **Refund and restock selected received returns**.
`complete_return()` runs inside a transaction and locks both the return request
and the order.

It refuses to complete a request that has not been received. Once received, it:

1. Calls the original payment provider refund boundary.
2. Restores deducted physical inventory once.
3. Sets order status to `returned`.
4. Sets payment status to `refunded`.
5. Sets fulfillment status to `returned`.
6. Stores refund reference and timestamp.
7. Sets return request status to `refunded`.
8. Stores completion time.

If the request is already refunded, the function returns without repeating the
refund or restock.

## State diagrams

```text
CANCELLATION
pending order -------------------------------> cancelled
paid + processing -> provider refund -> stock restored -> cancelled/refunded
shipment exists ------------------------------> cancellation rejected

RETURN
completed + delivered physical order
  -> requested
  -> approved OR rejected
  -> in_transit
  -> received
  -> provider refund + stock restored
  -> refunded / returned
```

## Important transaction boundary

The current learning implementation calls external refund APIs while inside a
database transaction. That keeps the local transition grouped, but a slow or
uncertain provider can hold a database lock. A production refinement would use
an outbox/background job:

```text
record refund intent locally
  -> worker calls provider
  -> store provider result
  -> retry safely with idempotency key
  -> complete stock/state transition
```

That is why background jobs and operations are later lessons.

## Debugging checklist

```text
cancel button gives 404       -> session/order-owner authorization
paid cancellation fails       -> provider refund configuration
shipped order cancels         -> shipment boundary was bypassed
stock increases twice         -> inventory state guard or row lock
return form appears too early -> eligibility rules are wrong
return approves twice         -> transition guard is missing
refund before item received  -> completion-state check is missing
bKash refund error            -> provider refund adapter is not implemented
```

## Files involved

- `shop/refunds.py`: cancellation and refund transitions.
- `shop/returns.py`: reverse-logistics state machine.
- `shop/payments.py`: provider refund boundary.
- `shop/inventory.py`: locked restoration and idempotency.
- `shop/views.py`: customer authorization and POST endpoints.
- `shop/admin.py`: staff shipment and return actions.
- `shop/models.py`: `ReturnRequest`, payment, inventory, and fulfillment fields.
- `shop/templates/shop/order_success.html`: customer cancellation and return UI.
