# Django Ecommerce 44: Postgres And Resend Deployment

This lesson switches the checkout lab from local-only services to production
infrastructure configuration.

## Goal

Use a separate Postgres database and Resend HTTP email delivery without
changing the Personal Dictionary service.

## What We Built

- `DATABASE_URL` support through `dj-database-url`
- Postgres driver through `psycopg[binary]`
- Separate checkout `RESEND_API_KEY` and `RESEND_FROM_EMAIL` settings
- Custom Resend email backend using HTTPS
- Console email fallback when Resend variables are absent
- WhiteNoise production static-file configuration
- Gunicorn and deployment dependencies
- Mocked Resend payload test with no network call

## Local Versus Production

```text
Local:
  SQLite + console email

Production:
  Checkout Postgres + Resend API + Gunicorn
```

The Dictionary service keeps its own `DATABASE_URL`, migrations, and Render
environment variables. The checkout service receives its own values even when
the variable names are the same.

## Render Environment

Add these to the checkout service only:

```text
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<long-random-checkout-secret>
DJANGO_ALLOWED_HOSTS=<checkout-hostname>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<checkout-hostname>
DATABASE_URL=<checkout-postgres-url>
RESEND_API_KEY=<checkout-resend-key>
RESEND_FROM_EMAIL=<verified-sender-address>
DEFAULT_FROM_EMAIL=<verified-sender-address>
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_HSTS_SECONDS=31536000
DJANGO_HSTS_INCLUDE_SUBDOMAINS=true
DJANGO_HSTS_PRELOAD=true
```

Do not commit these values or paste the API key into source files. Resend's
email API uses a Bearer token and the `/emails` endpoint; the sender address
must be verified in Resend before production delivery.

## Commands

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py collectstatic --noinput
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py check --deploy
```

For Render, use `pip install -r requirements.txt` as the build step and
`gunicorn mini_checkout_lab.wsgi:application` as the start command. Run
migrations as part of the release/deploy process before accepting traffic.

## Checkpoint

You understand:

- why each deployed service should have its own database
- how the same Resend account can serve separate applications safely
- why secrets belong in Render environment variables
- how Django switches backends from console to Resend
- why the Resend integration is tested without a live API call

## Next Project

The checkout lab is now production-configured. The next project is the
separate Chat Lab, which will teach conversations and real-time delivery.
