Yes, exactly. We should learn the real version for both systems.
Real shipping connection
Our Django app would connect to a courier’s merchant API like this:
Customer enters address
        ↓
Our server asks courier for a delivery quote
        ↓
Courier returns delivery cost and available service
        ↓
We show the customer the shipping option
        ↓
Customer completes payment, or chooses COD
        ↓
Our server creates a courier consignment
        ↓
Courier returns tracking/consignment ID
        ↓
We save that ID on our Order
        ↓
Courier sends status updates
For example, after payment we might send the courier:
{
  "merchant_order_id": "ORDER-1042",
  "recipient_name": "Sabital Hasan",
  "recipient_phone": "01700000000",
  "recipient_address": "Dhaka, Bangladesh",
  "item_quantity": 2,
  "item_weight": 0.8,
  "amount_to_collect": 0
}
The courier would return something like:
{
  "consignment_id": "PATHAO-ABC123",
  "status": "pending"
}
Then our database stores:
Order
  payment_status = paid
  fulfillment_status = shipment_created
  courier = Pathao
  tracking_code = PATHAO-ABC123
Later, the courier may notify our Django webhook:
pending → picked_up → in_transit → delivered
Pathao provides courier services for deliveries across Bangladesh, and its merchant ecosystem includes courier integration capabilities. We would use their current merchant/API access rather than inventing tracking ourselves. Pathao Courier · Pathao Commerce
Important: shipping price and courier price are not always the same
Suppose:
Customer pays shipping: BDT 100
Courier charges us: BDT 70
The remaining amount may cover handling or profit.
For cash on delivery:
Customer pays courier: product price + shipping
Courier later settles the money with the merchant
For prepaid orders:
Customer pays us online
Courier delivers the package
Courier collects nothing
That is why our future order needs separate values such as:
customer_shipping_amount
courier_shipping_cost
amount_to_collect
fulfillment_status
tracking_code
Real payment connection
A real payment provider works similarly:
Our server creates a payment session
        ↓
Provider returns a checkout URL or client secret
        ↓
Customer pays on the provider's secure page
        ↓
Provider processes card/mobile-wallet/bank payment
        ↓
Provider sends our server a signed webhook
        ↓
Our server verifies the webhook
        ↓
Order becomes paid
For a Stripe-style integration, one payment object is normally associated with one order or checkout session, and it moves through statuses until payment succeeds or fails. Stripe PaymentIntents Stripe also provides test payment details so we can practise without real money. Stripe testing
The key database fields would become:
Order
  payment_provider = "..."
  payment_method = "card" / "mobile_wallet" / "bank"
  payment_reference = "provider-payment-id"
  payment_status = pending / paid / failed / refunded
  paid_at = timestamp
We never store card numbers or CVV in our database.
The complete real-world flow
1. Customer adds product
2. Checkout calculates subtotal
3. Courier API calculates shipping
4. Customer selects shipping method
5. Order is created as pending
6. Payment session is created
7. Customer pays
8. Payment webhook is verified
9. Order becomes paid
10. Stock is deducted
11. Courier shipment is created
12. Tracking code is saved
13. Receipt email is sent
14. Courier status updates arrive through webhook
15. Customer sees delivered status
For Bangladesh, we should choose the payment gateway based on which merchant account you can actually open and which methods you need, such as cards, bKash, Nagad, or bank payments. We should not blindly build around Stripe until we confirm the provider supports your business/account country and settlement requirements; payment methods and availability depend on the account country. Stripe country specifications
So Lesson 47 should become more meaningful:
Lesson 47: Real Payment Sandbox
- real provider test checkout
- payment session creation
- success and failure handling
- signed webhook
- payment status verification
- duplicate webhook protection
Then we can build:
Lesson 48: Courier API And Fulfillment
- shipping quotes
- courier order creation
- tracking number
- shipment status webhook
- COD versus prepaid
- fulfillment dashboard
That will take us from “demo ecommerce” to a genuinely realistic ecommerce architecture.

===
We’ll build the project with:
- Real payment-session flow, using sandbox credentials
- Real webhook verification
- Real order and payment statuses
- Real shipping quotes and shipment creation
- Real tracking IDs and fulfillment states
- Environment variables for provider credentials
- Separate provider adapters, so we can switch from sandbox to live
- Idempotency protection, so repeated callbacks do not duplicate payments or shipments
- No card details stored in our database
The only things that will be fake during learning are:
Test payment credentials
Sandbox provider accounts
Test products and addresses
The architecture itself will be real. Later, going live should mostly mean changing:
PAYMENT_MODE=test  → live
PAYMENT_SECRET_KEY=test_key → live_key
COURIER_API_URL=sandbox → production
COURIER credentials=test → live
There may still be provider-specific setup, business verification, live webhook URLs, and local compliance requirements. But the Django code and database structure will already follow the real pattern.
So yes, we are aligned: we’ll build a production-shaped learning project, then swap test integrations for live integrations when the time comes.

====

Let’s begin with the payment lesson. We’ll keep the integration production-shaped: the order will create a provider checkout session, return from the provider, and only a verified webhook will mark it paid. I’m first checking the current project files and dependencies so this fits our existing checkout instead of creating a parallel flow.




Ran commands



I found an important boundary in our current code: shipping is already server-owned, but payment is still a direct “mark this order paid” view. For this lesson I’m going to introduce the real payment shape first: provider reference, payment method, checkout-session creation, and a webhook entry point, while keeping the existing demo path available for tests until we connect credentials.




Ran git status --short; Get-Content shop\templates\shop\order_success.html; Get-Content shop\admin.py; Get-ChildItem shop\migrations -File | Sort-Object Name | Select-Object -ExpandProperty Name in 3s




I’m making this first checkpoint deliberately small but real: the order will gain provider/payment identity fields, the app will have a payment-provider boundary, and Stripe Checkout/webhook routes will exist only when test credentials are configured. The existing demo payment remains available as a learning fallback, so we can verify the project locally without pretending a fake payment is a real charge.




The first edit attempt hit a path typo before changing anything. I’ve corrected the workspace path and am applying the same scoped checkpoint now; your personal words2.md remains untouched.




Edited files, ran a command



The first payment checkpoint is now in place and the existing suite still passes: 24 tests, no Django system-check issues. I’m doing one review pass now for migration/admin visibility and documenting exactly what is sandbox-ready versus what still requires provider credentials, so the lesson stays honest.




Edited files, ran commands



The architecture checkpoint is complete and the tests pass. One small practical note: the project now declares the Stripe SDK, but this virtual environment may not have installed the new dependency yet; I’m checking that separately before I hand you the exact next setup command.




Ran commands



Reconnecting /5





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





Reconnecting... waiting for network





The Stripe SDK is installed now. I’m adding focused tests for the two things that matter most here: starting a hosted checkout saves the provider reference, and a signed webhook changes the order to paid exactly once. That gives us a real safety net before any keys enter the picture.

Everything now passes with the new payment tests. I’m applying the migration to the local checkout database as the final step; no server will be left running afterward.