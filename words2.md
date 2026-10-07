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





The Stripe SDK is installed now. I’m adding focused tests for the two things that matter most here: starting a hosted checkout saves the provider reference, and a signed webhook changes the order to paid exactly once. That gives us a real safety net before any keys enter the picture.

Everything now passes with the new payment tests. I’m applying the migration to the local checkout database as the final step; no server will be left running afterward.

====
stripe impli >> 
====

You’re right. We should finish the Stripe sandbox connection before moving to Lesson 48. The code structure is ready, but we have not yet connected your actual test credentials and webhook.
We still need to complete this checklist:
1. Get a Stripe test-mode secret key:
STRIPE_SECRET_KEY=sk_test_...

https://dashboard.stripe.com/acct_1SKex0EmKunnQdQQ/test/apikeys?utm_source=chatgpt.com

2. Configure the project:
PAYMENT_PROVIDER=stripe
PAYMENT_CURRENCY=usd
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
Keep these in local environment variables or Render environment settings. Never commit them or send them here.
3. Start the local server:
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py runserver 8001
4. Forward Stripe events to Django using the Stripe CLI:
stripe listen --forward-to localhost:8001/payments/stripe/webhook/
Stripe CLI will display a webhook signing secret beginning with whsec_. That becomes STRIPE_WEBHOOK_SECRET.
5. Test the complete flow:
Create order
→ Click Pay securely
→ Stripe test checkout
→ Use a Stripe test card
→ Stripe sends checkout.session.completed
→ Django verifies the signature
→ Order becomes paid
→ Receipt is sent
Stripe’s Checkout flow uses a hosted Checkout Session, and the provider recommends using webhooks for fulfillment rather than trusting only the browser return page. Checkout Sessions · Stripe webhook endpoints
There is one small production detail we should handle before calling this payment lesson complete: support asynchronous payment events such as delayed success and failure. Our current code handles the normal successful card event, which is enough for the first sandbox test. After we verify that flow, we’ll add the async events and then move to Lesson 48.
So the planned order is:
Finish Stripe sandbox test
→ Add async payment success/failure handling
→ Verify receipt and database state
→ Begin physical fulfillment and courier tracking
We are not missing a new architectural lesson. We simply need to connect and verify the credentials now.



==



That error means the Stripe CLI is not installed. The Python stripe package and the stripe terminal command are two separate things.
In PowerShell, install the CLI globally:
winget install Stripe.StripeCLI
That is Stripe’s official Windows installation command. Stripe CLI repository
After installation, completely close and reopen the VS Code terminal, then verify:
stripe version
Next, authenticate:
stripe login
Your browser will open so you can authorize the CLI. Then use one terminal for the webhook listener:

stripe listen --api-key="$env:STRIPE_SECRET_KEY" --events="checkout.session.completed" --forward-to="http://127.0.0.1:8001/payments/stripe/webhook/"

It will print something like:
Your webhook signing secret is whsec_...

in another terminal >> 
In a PowerShell terminal, configure Django using your own test values:
$env:PAYMENT_PROVIDER="stripe"
$env:PAYMENT_CURRENCY="usd"
$env:STRIPE_SECRET_KEY="sk_test_your_key_here"
$env:STRIPE_WEBHOOK_SECRET="whsec_secret_from_stripe_listen"

You can verify the non-secret settings safely:


$env:PAYMENT_PROVIDER
$env:PAYMENT_CURRENCY

if ($env:STRIPE_WEBHOOK_SECRET) {
    Write-Host "Stripe webhook is loaded"
} else {
    Write-Host "Stripe webhook is missing"
}

if ($env:STRIPE_SECRET_KEY) {
    Write-Host "Stripe key is loaded"
} else {
    Write-Host "Stripe key is missing"
} 


It should print:
stripe
usd
Then:
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py runserver 8001
Now create a new order:
Add product
→ Cart
→ Checkout
→ Place order
→ Order success page
Do not paste either secret here or commit them. After that, the Pay securely button should redirect you to Stripe’s test checkout, and the CLI will forward the payment webhook back to Django.


imp>> 
The two terminals are:
Django server: http://127.0.0.1:8001
Stripe listener: 

Card:
4242 4242 4242 4242

Expiry:
Any future date

CVC:
Any 3 digits

ZIP:
Any number

====

Render Production Webhook Setup >>>>

https://dashboard.stripe.com/test/webhooks

+ Add destination

Event destination scope: Your account
Payload style: Snapshot
Select event: checkout > checkout.session.completed

Destination name: mini-checkout-render-webhook

Endpoint URL (Important)
In the Endpoint URL box, enter your Render webhook URL.
It should look like:
https://YOUR-RENDER-APP-NAME.onrender.com/payments/stripe/webhook/

Example:
https://mini-checkout-lab.onrender.com/payments/stripe/webhook/


Description (optional)
You can write:
Django Stripe checkout payment completion webhook

or leave it empty.
Click:
Create destination

====
les48>>
In your Stripe Dashboard webhook endpoint, enable these three events:

checkout.session.completed
checkout.session.async_payment_succeeded
checkout.session.async_payment_failed

=====

I found your notes and the current state. We already have shipping method selection and inventory deduction, but shop/shipping.py is still only pricing logic; there is no shipment record, courier adapter, tracking state, or webhook update yet. I’m going to add that missing layer in a provider-neutral way first, so later a Pathao/DHL/FedEx integration replaces one adapter instead of rewriting the order system.

The lesson will have two parts: a durable Shipment record tied to each order, and a courier-provider boundary with a local sandbox adapter. That lets us demonstrate the full state flow today (paid → ready → shipment created → in transit → delivered) while keeping the database contract ready for a real courier API later. I’m editing the model, service, admin workflow, customer status page, and tests together so the pieces stay consistent.

The core fulfillment layer is in place now: paid orders can become “ready,” admins can create a sandbox shipment, the system stores a provider reference and tracking number, and shipment status changes update the order automatically. I’m running Django’s checks and migration generation next; this is where we catch any model/admin wiring mistakes before we document the lesson.

Checks are clean: the project now has 32 passing tests, including shipment creation, duplicate protection, and tracking-status transitions. I’m doing one final review of the generated migration and diff, then I’ll give you the exact admin exercise for today so you can see the fulfillment lifecycle yourself.

====

Yes, exactly. Shipping providers connect through APIs much like Stripe.
How courier integration works
Customer places order
→ Stripe/bKash confirms payment
→ Our system deducts inventory
→ Our server calls courier API
→ Courier creates a consignment
→ Courier returns tracking number
→ We save it in Shipment
→ Courier sends status updates through webhook
→ Our order becomes delivered
Our courier request would contain information such as:
Merchant/order reference
Customer name and phone
Delivery address
Package weight
COD amount or prepaid amount
Product description
The courier returns something like:
consignment_id: "PT123456"
tracking_code: "PT123456"
status: "Pending"
Then we save that information and show it to the customer.
Pathao officially advertises a Developer API and webhook integration with a callback URL and secret. Their merchant onboarding is handled through the Pathao merchant platform. Pathao Developer API and webhook announcement, Pathao Merchant Portal
For courier sandboxes, it depends on the provider. Some offer test credentials or a test account, while others only provide API access after merchant approval. I could verify Pathao’s API and webhook availability, but I did not find a clearly public sandbox environment, so we should not invent one. We can keep our current manual sandbox provider for local testing until Pathao gives us credentials.
bKash later
Yes, we can absolutely add bKash webhooks in the future.
The flow would be:
Our server requests a bKash payment
→ Customer is redirected to bKash checkout
→ bKash returns payment information
→ Our server verifies/query-checks the payment
→ bKash sends a notification/webhook
→ We mark the order paid
→ Inventory and fulfillment begin
→ Receipt is sent
bKash provides a demo merchant portal for testing Checkout, Tokenized Checkout, and webhook notifications. bKash Demo Merchant Portal
We should build bKash as another payment adapter beside Stripe:
StripePaymentProvider
BkashPaymentProvider
ManualPaymentProvider
All of them should eventually produce the same internal result:
payment_status = paid
payment_provider = stripe or bkash
payment_reference = provider transaction ID
That means fulfillment does not care whether the customer paid through Stripe or bKash. It only begins after our backend verifies that the payment succeeded.






https://merchant.pathao.com/courier/dashboard



====

Lesson 51 is wired :3
We added a real PathaoCourierProvider that can:
1. Request a Pathao access token.
2. Build a consignment request.
3. Send the paid order to Pathao.
4. Save the returned consignment/tracking reference in Shipment.
The provider is still disabled by default:
FULFILLMENT_PROVIDER=manual
To use Pathao deliberately, configure:
FULFILLMENT_PROVIDER=pathao
PATHAO_BASE_URL=your_base_url
PATHAO_CLIENT_ID=your_client_id
PATHAO_CLIENT_SECRET=your_client_secret
PATHAO_USERNAME=your_username
PATHAO_PASSWORD=your_password
PATHAO_STORE_ID=your_store_id
PATHAO_SENDER_NAME=your_store_name
PATHAO_SENDER_PHONE=your_phone

In PowerShell, set your credentials temporarily in the same terminal:
$env:PATHAO_BASE_URL="https://courier-api-sandbox.pathao.com"
$env:PATHAO_CLIENT_ID="7N1aMJQbWm"
$env:PATHAO_CLIENT_SECRET="wRcaibZkUdSNz2EI9ZyuXLlNrnAv0TdPUPXMnD39"
$env:PATHAO_USERNAME="test@pathao.com"
$env:PATHAO_PASSWORD="lovePathao"

        The problem is not the city, zone, or area IDs yet. The problem is that the sandbox server itself is returning:
        522 Connection timed out
        You confirmed this with both:
        Invoke-RestMethod ...
        and:
        curl https://courier-api-sandbox.pathao.com
        So Pathao’s sandbox API is currently unreachable. Until the token endpoint responds, we cannot request the city list.
        When it becomes available, the order will be:
        Issue token
        → Request city list
        → Select city ID
        → Request zone list
        → Select zone ID
        → Request area list
        → Select area ID
        Use this corrected request when trying again:
        $tokenBody = @{
        client_id = $env:PATHAO_CLIENT_ID
        client_secret = $env:PATHAO_CLIENT_SECRET
        username = $env:PATHAO_USERNAME
        password = $env:PATHAO_PASSWORD
        grant_type = "password"
        } | ConvertTo-Json

        $tokenResponse = Invoke-RestMethod `
        -Uri "$env:PATHAO_BASE_URL/aladdin/api/v1/issue-token" `
        -Method Post `
        -ContentType "application/json" `
        -Body $tokenBody

        $tokenResponse | ConvertTo-Json -Depth 10
        For now, keep:
        FULFILLMENT_PROVIDER=manual

PATHAO_RECIPIENT_CITY_ID=...
PATHAO_RECIPIENT_ZONE_ID=...
PATHAO_RECIPIENT_AREA_ID=...
You collected the authentication credentials. We still need the store ID and recipient city/zone/area IDs, because Pathao requires structured location IDs rather than only "Dhaka" as text.
Pathao confirms that API integration is available through the Merchant Panel’s Developer API section, and its current integration flow supports API credentials plus webhook configuration. Pathao Developer API help, Pathao API and webhook information
The manual sandbox remains available, so we won’t accidentally create real deliveries during testing. Django checks pass and all 32 tests pass.
Next lesson: Pathao webhook integration, where courier status updates will automatically change our shipment from Created to In transit, Delivered, or Exception.

=====
We don’t need to stop the project because Pathao’s sandbox is temporarily unreachable.
What we do now
1. Keep local fulfillment on:
FULFILLMENT_PROVIDER=manual
2. Continue with the next lesson: Pathao webhook handling.
We can build and test the webhook locally using mocked Pathao events:
Pathao sends status update
→ Our webhook verifies the secret
→ Shipment status changes
→ Order status changes
3. Add proper address mapping afterward:
Customer selects city
→ Customer selects zone
→ Customer selects area
→ We send Pathao’s IDs
This is better than guessing IDs or storing only "Dhaka" as text.
4. Retry the Pathao sandbox later. If it still returns 522, contact Pathao support and ask:
Is https://courier-api-sandbox.pathao.com currently available, and where can I retrieve the city, zone, and area lists for the sandbox API?

So our path is:
Manual sandbox fulfillment
→ Build webhook logic
→ Build address ID selection
→ Retry Pathao API
→ Switch provider from manual to pathao
Nothing is broken in our project. The blocker is only Pathao’s sandbox server response.