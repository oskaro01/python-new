# Mini Checkout Lab: Fulfillment Lifecycle

Payment answers “did money get verified?” Fulfillment answers “what do we
deliver, and what state is it in now?” The application supports digital,
physical, and hybrid products, so fulfillment branches after payment.

## The complete branch

```text
verified payment
  -> inventory decision
  -> digital download OR physical shipment OR both
  -> delivery/status updates
  -> order completed
```

The order, inventory, fulfillment, and shipment statuses remain separate so a
paid order can be visible as processing while a courier is still delivering.

## 1. Payment calls fulfillment

After demo, Stripe, or bKash confirmation, the payment code calls:

```python
deduct_paid_order_inventory(order)
mark_order_ready_for_fulfillment(order)
enqueue_receipt_job(order)
```

This means fulfillment starts only after the server has verified payment. A
customer redirect alone cannot unlock a file or create a shipment.

## 2. Inventory decision

`Product.product_type` controls the branch:

```text
digital  -> no physical stock required
physical -> stock must be deducted
hybrid   -> stock must be deducted and a digital file may be delivered
```

For a digital-only order, the inventory status becomes
`not_required`. For physical or hybrid items, the helper loads the ordered
products and locks them with `select_for_update()` inside a transaction.

The lock protects concurrent orders competing for the same stock:

```text
enough stock -> subtract quantities, mark deducted
not enough   -> mark unavailable, do not pretend fulfillment is ready
```

The helper also refuses to deduct twice when the same payment callback is
repeated. `inventory_deducted_at` records when the subtraction happened.

## 3. Fulfillment status after inventory

`mark_order_ready_for_fulfillment()` translates inventory into business state:

```text
digital-only            -> fulfillment not_required, order completed
physical stock deducted -> fulfillment ready, order processing
stock unavailable       -> no successful transition
```

Digital delivery can be available immediately after payment. Physical orders
need a shipment record and later courier statuses.

## 4. Physical shipment creation

`create_shipment_for_order(order)` runs inside a transaction and locks the
order. It rejects an order when:

```text
payment is not paid
stock is unavailable
the order is digital-only
inventory has not been deducted
the shipping address is incomplete
```

It also checks whether the order already has a `Shipment`. If it does, the
existing record is returned instead of creating a second consignment.

The courier adapter returns a common `ShipmentResult`:

```text
provider
provider_reference
tracking_number
tracking_url
provider_payload
```

The application saves those values in a separate one-to-one `Shipment` row and
sets the order's fulfillment status to `shipment_created`.

The order does not store every courier-specific field. The provider payload is
kept with the shipment, while the order keeps the business-level state.

## 5. Manual courier provider

The default setting is:

```env
FULFILLMENT_PROVIDER=manual
```

The manual provider behaves like a courier adapter without making a network
request. It creates values such as:

```text
provider = manual
tracking_number = DEMO-000023
provider_reference = manual-order-23
```

This lets Admin simulate the full lifecycle safely:

```text
create shipment
-> created
-> in_transit
-> out_for_delivery
-> delivered
```

## 6. Courier status updates

`update_shipment_status(shipment, status)` validates the status choice, locks
the shipment and related order, and saves the new state.

It records timestamps only once:

```text
in_transit or out_for_delivery -> shipped_at
delivered                      -> delivered_at
```

Then it maps shipment status to order status:

```text
created          -> shipment_created / processing
in_transit      -> in_transit / processing
out_for_delivery -> out_for_delivery / processing
delivered       -> delivered / completed
exception       -> exception / processing
```

The status update is idempotent enough to accept repeated provider updates
without recreating the shipment or changing an already-recorded timestamp.

## 7. Pathao provider boundary

Changing the setting to:

```env
FULFILLMENT_PROVIDER=pathao
```

selects `PathaoCourierProvider`. The checkout and order code do not need to
know Pathao's API details; the adapter implements the same
`create_shipment(order)` contract as the manual provider.

The adapter:

1. Requests a Pathao access token with merchant credentials.
2. Calculates item count and total weight from `OrderItem` product data.
3. Builds the recipient and sender payload.
4. Sends a consignment request to Pathao.
5. Extracts the returned consignment/tracking reference.
6. Returns a `ShipmentResult` for the shared persistence code.

Pathao requires structured city, zone, and area IDs. A free-form address is
not enough for those fields, which is why the current adapter reads configured
IDs. A later checkout improvement should let the customer choose a validated
address instead of using deployment-wide defaults.

If Pathao credentials, sender details, or location IDs are missing, the adapter
fails before creating a real shipment. The manual provider remains the safe
local default.

## 8. Digital fulfillment

Admin uploads a product's digital file. The order item stores the filename at
purchase time:

```text
OrderItem.digital_file_name
```

That snapshot prevents a later product edit from silently changing an old
order's purchased file.

The success view creates download links only when:

```text
order.payment_status == paid
item is digital or hybrid
item has a stored filename
```

`build_download_url()` creates a signed token containing only the order and
item IDs. The token is time-limited by `DIGITAL_DOWNLOAD_MAX_AGE`.

The download request is:

```text
GET /orders/<order_id>/items/<item_id>/download/?token=...
```

The view verifies, in order:

1. Django signature and expiry.
2. Token order ID and item ID match the URL.
3. The item belongs to that order.
4. The item is digital or hybrid.
5. The order is paid.
6. A filename exists in storage.

Only then does Django open the file through `default_storage` and stream it as
an attachment. The private storage path is never published as a public media
URL.

Render's local filesystem is ephemeral, so production digital fulfillment
needs private object storage such as S3-compatible storage. The view can keep
using Django's storage API after that change.

## Fulfillment state machine

```text
paid order
   |
   +-- digital only -----------------> download token -> file stream
   |
   +-- physical/hybrid
          -> stock lock and deduction
          -> fulfillment ready
          -> shipment created
          -> in transit
          -> out for delivery
          -> delivered / order completed
```

## Debugging checklist

```text
paid but no download       -> item type, filename, payment status, token
download exposes a file    -> storage must remain private
shipment rejected          -> payment, inventory, address, or product type
duplicate shipment         -> missing one-to-one/idempotency check
stock deducted twice       -> inventory lock or state guard
Pathao fails before API    -> credentials, sender, store, or location IDs
tracking never changes     -> courier callback/poll mapping
order stays processing     -> shipment status never reached delivered
```

## Files involved

- `shop/inventory.py`: stock locks, deduction, and restoration.
- `shop/shipping.py`: manual/Pathao adapters and shipment transitions.
- `shop/downloads.py`: signed expiring download tokens.
- `shop/views.py`: payment-to-fulfillment calls and protected downloads.
- `shop/models.py`: `Shipment`, inventory, and fulfillment fields.
- `shop/admin.py`: local shipment creation and status simulation.
- `shop/settings.py`: fulfillment provider and private storage configuration.
