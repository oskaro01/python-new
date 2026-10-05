# Django Ecommerce 43: Tests, Security And Deployment

This lesson closes the Mini Checkout Lab with a production-readiness pass.

## Goal

Protect state-changing actions, verify the important checkout flows, and make
deployment configuration explicit without deploying the lab yet.

## What We Built

- POST-only endpoint coverage
- CSRF enforcement coverage
- Security-header coverage
- Environment-controlled HTTPS and cookie settings
- HSTS, referrer-policy, content-sniffing, and frame protections
- `requirements.txt` with Django and Gunicorn
- Deployment checklist
- `check --deploy` verification

## Security Settings

Production values are provided through environment variables:

```text
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<long-random-secret>
DJANGO_ALLOWED_HOSTS=example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_HSTS_SECONDS=31536000
DJANGO_HSTS_INCLUDE_SUBDOMAINS=true
DJANGO_HSTS_PRELOAD=true
```

Local development keeps HTTPS-only behavior disabled so `localhost` remains
easy to use.

## Deployment Checklist

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py collectstatic --noinput
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py test shop
.\.venv\Scripts\python.exe my_python_work\web_practice\03_mini_checkout_lab\manage.py check --deploy
```

For a hosted service, configure the environment variables in the provider's
secret settings, use the project `requirements.txt`, run migrations during
release, and serve the WSGI application with Gunicorn.

This lab is separate from the deployed Personal Dictionary service and is not
being deployed as part of this lesson.

## Test Coverage

The suite now checks:

- catalog, cart, checkout, order, payment, and receipt behavior
- POST-only state changes
- CSRF protection on cart mutation
- session ownership of order actions
- security response headers
- receipt content and duplicate-send prevention

## Checkpoint

You understand:

- why security defaults belong in settings and environment configuration
- why tests should protect behavior at the boundary
- why deployment checks require production-like values
- why migrations, static files, and dependencies are deployment concerns
- why preparing a project is different from deploying it

## Next Step

The Mini Checkout Lab is complete. The next project in the learning path is
the separate Chat Lab, where messaging will teach conversations, ownership,
and later real-time delivery.
