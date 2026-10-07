# Django Ecommerce 51: Pathao Courier API

This lesson connects our provider boundary to the Pathao Merchant API while
keeping the manual sandbox provider available for safe local practice.

## Provider Selection

The application remains safe by default:

```env
FULFILLMENT_PROVIDER=manual
```

Only switch to Pathao when the credentials and address IDs are configured:

```env
FULFILLMENT_PROVIDER=pathao
PATHAO_BASE_URL=https://courier-api-sandbox.pathao.com
PATHAO_CLIENT_ID=your-client-id
PATHAO_CLIENT_SECRET=your-client-secret
PATHAO_USERNAME=your-merchant-username
PATHAO_PASSWORD=your-merchant-password
PATHAO_STORE_ID=your-store-id
PATHAO_SENDER_NAME=Your Store
PATHAO_SENDER_PHONE=017XXXXXXXX
PATHAO_RECIPIENT_CITY_ID=1
PATHAO_RECIPIENT_ZONE_ID=1
PATHAO_RECIPIENT_AREA_ID=1
```

Never commit these values. Store them in local environment variables and in
Render's private environment settings.

## What the Adapter Does

1. Requests a Pathao access token using the merchant credentials.
2. Builds a consignment request from the paid order, recipient, package count,
   weight, and address IDs.
3. Creates the order through Pathao.
4. Saves the returned consignment/tracking reference in `Shipment`.

Pathao requires structured location IDs rather than only a free-form city
string. That is why the first version uses configured city, zone, and area IDs.
The next refinement should add proper address selection to checkout instead of
using deployment-wide defaults.

## Sandbox And Production

Use the sandbox base URL while learning. Switch to the live base URL only after
merchant approval and a deliberate deployment review. Keep the `manual`
provider available so tests never create real courier consignments.

Pathao's official help identifies the Developer API inside the Merchant Panel,
and Pathao documents API credentials and webhook configuration for system
integration. The exact available environment and location data should be taken
from the Developer API panel for the merchant account being used.

## Verification

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py check
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
```

Do not create a real shipment until the Pathao account, pickup address, store
ID, location IDs, and API environment have been verified.

## Next Lesson

Lesson 52 will add the Pathao webhook endpoint, verify its shared secret, and
map courier status callbacks to our `Shipment` and `Order` records.
