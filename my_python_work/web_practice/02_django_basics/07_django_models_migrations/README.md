# Django Basics 07: Models And Migrations

Now we create the first real database model for the dictionary direction.

## Big Idea

```text
Model = Python class that describes database data
Migration = database change plan created from models 
Database table = where rows are stored

```

## Why A New App?

We already have a `pages` app for simple pages.

Dictionary words are a different feature area, so we create a separate app:

```text
dictionary
```

That keeps the project cleaner:

```text
pages = home/about pages
dictionary = word data and dictionary features
```

## Files Added Or Changed

```text
02_first_django_project/
    mini_site/
        settings.py
    dictionary/
        __init__.py
        admin.py
        apps.py
        models.py
        migrations/
            __init__.py
            0001_initial.py
```

## The Word Model

`dictionary/models.py` contains a `Word` class. It describes one dictionary
entry. When saved, each `Word` object becomes one row in a database table.

The model stores:

- word
- meaning
- example
- category
- favorite status
- created time
- updated time

For example, one row could contain `word="curious"`,
`meaning="wanting to learn"`, and `is_favorite=False`.

`blank=True` lets a form leave a field empty. `default=False` makes a new
word not a favorite unless you choose otherwise. Django fills in `created_at`
and `updated_at` automatically. `Meta.ordering = ["word"]` sorts results by
word by default, and `__str__` makes Django display the word itself when it
needs a readable name for an entry.

## What The Other Files Do

- `dictionary/apps.py` names the dictionary app; `settings.py` adds it to
  `INSTALLED_APPS` so Django loads it.
- `dictionary/migrations/0001_initial.py` is the first database change plan.
  Its `CreateModel` operation tells Django to create the Word table and fields.
- `dictionary/admin.py` registers `Word` in Django's admin area. It chooses
  the columns, filters, search fields, and ordering shown there.
- The `__init__.py` files mark the Python packages. You do not need to put
  lesson logic in them.

The admin setup does not automatically put words on our own pages. We will
connect the New Word form to the database in the next lesson.

## Commands

Create a migration:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py makemigrations dictionary
```

We already have `0001_initial.py`, so you do not need to create it again for
this lesson. `makemigrations` makes a new plan when the model changes later.

Apply migrations to the SQLite database:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py migrate
```

`migrate` follows the migration plan and creates the table in SQLite. Until
you run it, the model exists in Python but its table does not exist in the
database yet. Running `migrate` also sets up Django's built-in tables.

## Check Without Applying Database Changes

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check
```

Check that no new migration changes are waiting:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py makemigrations --check --dry-run
```

## Key Memory Hook

```text
models.py changes Python
makemigrations creates the plan
migrate changes the database
```

## Next Lesson

Next we will save the new-word form into the database.
