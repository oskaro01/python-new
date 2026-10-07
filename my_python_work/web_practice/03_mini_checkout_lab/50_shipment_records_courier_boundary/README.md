# Django Ecommerce 50: Shipment Records And Courier Boundary

This lesson begins physical fulfillment. Payment and stock are now separate
from delivery: a paid order with deducted inventory becomes ready for a
shipment, and a courier shipment gets its own tracking record.

## Real-World Flow

```text
verified payment
  -> inventory deducted
  -> order ready for fulfillment
  -> courier consignment created
  -> tracking number saved
  -> courier status callbacks/polls
  -> delivered
```

The important design choice is that the order does not store every courier
detail directly. `Shipment` stores the provider name, provider reference,
tracking number, tracking URL, current status, timestamps, and the raw provider
payload. A real courier adapter can therefore be added without changing the
checkout or payment code.

The Admin page shows three related but separate lifecycles:

- **Order status** answers whether the order is pending, being processed,
  completed, or cancelled.
- **Payment status** answers whether money is pending, paid, failed, or
  refunded in a future lesson.
- **Fulfillment status** answers whether delivery is ready, shipped, in
  transit, or delivered.

After this lesson, a paid physical order being shipped should show `Processing`
and `Delivered` should eventually move it to `Completed`.

## What We Built

- `Order.fulfillment_status` for the customer-facing delivery lifecycle
- A one-to-one `Shipment` model for courier data
- A provider boundary in `shop/shipping.py`
- A local `manual` sandbox provider that creates tracking numbers such as
  `DEMO-000023`
- Idempotent shipment creation: the same order cannot create two shipments
- Status synchronization for `created`, `in_transit`, `out_for_delivery`,
  `delivered`, and `exception`
- Admin action: select paid, stocked orders and choose **Create sandbox shipment**
- Admin status editing to simulate courier updates while learning

## Why This Is Not Yet a Real Courier Connection

The local provider deliberately does not pretend to call Pathao, DHL, FedEx,
or another carrier. Real courier APIs require merchant credentials, pickup
address configuration, service-area IDs, package dimensions/weight, and often
account approval. This lesson establishes the contract those providers must
implement.

The provider setting is:

```env
FULFILLMENT_PROVIDER=manual
```

Later, `manual` can be replaced by a real adapter after we verify the chosen
courier's current official API and sandbox requirements.

## Practice Checkpoint

1. Run migrations and tests.
2. Create or pay a physical order with available stock.
3. In Django Admin, open Orders, select the paid order, and choose
   **Create sandbox shipment**.
4. Open the Shipment record and change its status from `Created` to `In
   transit`, then `Out for delivery`, then `Delivered`.
5. Reload the order success page and observe the fulfillment status and tracking
   number.

## Verification

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
```

## Next Lesson

Lesson 51 will connect this provider boundary to a real courier API and map
our address/package data to the carrier's consignment request.
