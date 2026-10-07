# Django Ecommerce 52: Secure Digital Fulfillment

This lesson delivers digital products only after verified payment without
publishing their storage URL.

## Flow

```text
admin uploads private product file
  -> order snapshots the storage filename
  -> payment is verified
  -> server signs an expiring download token
  -> customer requests the protected download view
  -> server verifies token, order, item, and payment
  -> file streams as an attachment
```

## Security Rules

- Unpaid orders receive no download link.
- Tokens are signed with Django's secret key and cannot be edited.
- Tokens expire after `DIGITAL_DOWNLOAD_MAX_AGE` seconds (24 hours by default).
- The token is tied to one order and one order item.
- Files are opened through Django storage and are not served from a public
  media URL.
- The order item keeps a filename snapshot, so later product edits do not
  silently change what an existing customer purchased.

## Local Practice

1. Open Django Admin and create a `Digital` or `Physical + digital` product.
2. Upload a small test file in **Digital file**.
3. Purchase and pay for the product.
4. Reload the order page and use **Download**.
5. Confirm an unpaid order does not show the download section.

Local files are stored under `private_media/`, which is intentionally not
served as a public media directory.

## Production Note

Render's local filesystem is ephemeral. Before selling real downloads, use a
private persistent object store such as Amazon S3 or another compatible
service. The protected Django view can continue using the storage API, or it
can issue short-lived provider download URLs.

## Pending Integrations

- Pathao location lookup and webhook completion are pending while its sandbox
  returns HTTP `522`.
- bKash sandbox checkout and payment webhook remain on the roadmap.

## Next Lesson

Lesson 53 will add customer accounts and order history so customers can return
later and regenerate authorized download links.
