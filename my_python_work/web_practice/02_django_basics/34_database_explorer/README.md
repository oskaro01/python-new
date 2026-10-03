# Django Basics 34: Visual Database Explorer

This lesson adds a protected, read-only page that shows the structure of the
active database connection.

Open:

```text
/staff/database/
```

The page requires the existing `dictionary.view_all_words` permission. The
staff dashboard links to it, and users with that permission see a `Database`
link in the navigation.

## What The Page Reads

The explorer uses Django's database introspection API. It does not guess the
schema from the Python models.

It displays:

- every visible table, view, or partition
- the mapped Django model when one exists
- row count at page-load time
- every column
- the database type
- the Django field type
- nullable status
- database default
- primary-key and auto-increment markers
- foreign-key targets
- constraints and indexes
- a relationship map
- available, applied, and pending migrations
- applied migration history and timestamps

When the active backend is PostgreSQL, column types come from PostgreSQL's
catalog using `format_type`, so values such as `character varying(80)` and
`timestamp with time zone` reflect the real database type.

## What It Does Not Show

The page intentionally does not show:

- word meanings or other row contents
- password hashes
- database URLs
- database usernames or passwords
- Resend keys
- arbitrary SQL input

This makes the page useful for learning structure without creating a new
secret or data-leak surface.

## Understanding The Dictionary Tables

The important application relationships look like this:

```text
auth_user
  ├──< dictionary_category.owner_id
  └──< dictionary_word.owner_id

dictionary_category
  └──< dictionary_word.category_id
```

The actual page is generated from the live database, so it also includes
Django's support tables such as permissions, sessions, migrations, and admin
logs.

## Migration Status

The page compares two things:

```text
migration files in the project
records in the database's django_migrations table
```

The three numbers mean:

```text
available -> migration files Django knows about in code
applied   -> migrations recorded as completed in the database
pending   -> migrations still waiting to be applied
```

The normal workflow is:

```powershell
python manage.py makemigrations
python manage.py migrate
```

`makemigrations` notices model changes and creates migration instructions in
an app's `migrations/` folder. It does not change PostgreSQL yet.

`migrate` reads those instructions, changes the database schema, and records
the completed migration in `django_migrations`.

The explorer is deliberately read-only. It reports pending migrations but
does not run `migrate` from a browser request. Schema changes should happen
through the deployment build step or an intentional terminal command.

## Local And Production

Locally, the page reads SQLite because that is the local default.

On Render, the same code reads Neon PostgreSQL through `DATABASE_URL`.
Therefore the displayed types may differ between local and production, which
is exactly the point of this lesson: the database is the source of truth for
its own physical schema.

## Verification

Run:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py check
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py test pages accounts
```

Then deploy and open:

```text
https://personal-dictionary-ngm1.onrender.com/staff/database/
```

## What We Learned

```text
model definition -> Django's intended structure
migration        -> instructions that create/change structure
database schema  -> structure that actually exists
introspection    -> reading that real structure safely
```

## Next Lesson

Next: review and clean up the full Django learning project before the optional
ecommerce business module.
