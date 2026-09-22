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

The first model stores:

- word
- meaning
- example
- category
- favorite status
- created time
- updated time

## Commands

Create a migration:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py makemigrations dictionary
```

Apply migrations to the SQLite database:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py migrate
```

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

