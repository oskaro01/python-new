# Django Basics 35: Project Review And Cleanup

This lesson is the closing checkpoint for the Django dictionary project.

The goal is not to add a big feature. The goal is to make sure the project is
understandable, deployed, tested, and ready to rest before the next phase.

## What We Reviewed

The dictionary app now covers the main full-stack Django path:

- database models and migrations
- CRUD pages
- search and pagination
- forms and validation
- register, login, logout, password reset, and password change
- private user-owned words
- categories with a foreign key
- permissions and groups
- Django admin
- import/export
- testing
- security settings
- Render deployment with Neon PostgreSQL
- production logs and custom error pages
- database performance basics
- caching basics
- Resend email API
- health checks
- visual database explorer

## Cleanup Done

We removed the unused `Word.is_favorite` field.

Earlier, favorites were considered as a possible feature. Later we decided to
keep the dictionary app lighter, so the field stayed in the database without a
real workflow.

Files changed:

```text
dictionary/models.py
dictionary/admin.py
dictionary/migrations/0006_remove_word_is_favorite.py
```

That migration removes the column from the real database when `migrate` runs.

## Why This Needs A Migration

Changing `models.py` changes Django's intended structure.

The database does not change until a migration is applied:

```text
models.py change
    -> makemigrations creates 0006_remove_word_is_favorite.py
    -> migrate removes the database column
    -> django_migrations records that 0006 was applied
```

After deployment, the Database Explorer should show that `dictionary_word` no
longer has `is_favorite`.

## What We Kept

We kept the password-reset email logs because they are production-safe:

```text
recipient domain
eligible user count
provider result
```

They do not print reset tokens, full email contents, API keys, passwords, or
database URLs. They helped us debug Render and Resend, and they remain useful
for future delivery issues.

## Review Checklist

Run:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py check
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py test pages accounts
```

After deploying, check:

```text
/health/
/staff/
/staff/database/
/accounts/password-reset/
```

## Current Project Shape

The dictionary project is now a solid learning app, not a bloated product.

It deliberately avoids:

- payments
- shipping
- carts
- complex tagging
- social features

Those belong in the optional `mini_checkout_lab`, where they can be learned
without making the dictionary app heavy.

## Next Lesson

Next: rest, review the README files, then start the optional ecommerce
business module when you want to learn carts, checkout, shipping, orders, and
receipt emails.
