# Django Basics 26: Security Hardening

This lesson makes the project safer to configure and explains the main web
security rules we have already been using.

## What Changed

- Secret key can come from `DJANGO_SECRET_KEY`.
- Debug mode can come from `DJANGO_DEBUG`.
- Allowed hosts can come from `DJANGO_ALLOWED_HOSTS`.
- HTTPS-only options can be enabled for production.
- Basic response security headers are enabled.
- Import files are limited to 1 MB and 5,000 rows.
- `.env.example` documents production-style values without storing a real secret.

The local defaults still let us run the project normally.

## Environment Variables

The real `.env` file is ignored by Git. In deployment, set values in the
hosting provider's environment settings.

```text
DJANGO_SECRET_KEY
    private random value used to sign sessions and security tokens

DJANGO_DEBUG
    False in production

DJANGO_ALLOWED_HOSTS
    domains allowed to serve the project

DJANGO_SECURE_SSL_REDIRECT
    redirects HTTP to HTTPS when the site has HTTPS

DJANGO_SESSION_COOKIE_SECURE
DJANGO_CSRF_COOKIE_SECURE
    send those cookies only over HTTPS
```

For local learning, we leave the HTTPS settings off because the development
server uses plain `http://127.0.0.1:8000`.

## Security Rules We Are Using

### CSRF

Every form that changes data includes:

```html
{% csrf_token %}
```

CSRF protection helps stop another website from secretly submitting a form
using your logged-in browser.

### XSS

Django templates escape normal variable output by default. We do not use
`|safe` on user-entered word meanings or examples.

### SQL Injection

We use Django QuerySets instead of joining user input into SQL strings:

```python
Word.objects.filter(meaning__icontains=query)
```

### Authentication And Permissions

- `login_required` protects private pages.
- Owner filters protect each user's words.
- `permission_required` protects the staff dashboard.
- Passwords are handled by Django's password hashing system.

### Upload Safety

The import flow checks:

- file extension
- UTF-8 text
- maximum file size
- maximum row count
- JSON shape or CSV headers
- valid Word form data

The owner always comes from `request.user`, never from the uploaded file.

## Deployment Check

Run Django's deployment checklist:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check --deploy
```

Warnings are expected while using the local development server. Before real
deployment, set a private secret, turn off debug, configure allowed hosts,
enable HTTPS, and use a real production email/database setup.
===
 check --deploy showed expected warnings because we are still using local development defaults: DEBUG=True, HTTP, and the learning-only secret key

## Key Memory Hook

```text
Never trust input.
Never expose secrets.
Protect every boundary.
```

## Files

- `mini_site/settings.py`: environment-based security settings.
- `.env.example`: names of production configuration values.
- `pages/import_export.py`: import limits and validation.

## Next Lesson

Next: Render deployment preparation.
