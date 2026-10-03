# Django Basics 29: Database Performance

This lesson introduces two practical ways to keep database-backed pages
efficient:

```text
indexes
select_related
```

The goal is not to optimize everything blindly. The goal is to understand
which database work a page actually needs.

## What Is An Index?

Without an index, a database may inspect many rows to find matching data.

An index is an extra lookup structure that helps the database find rows
faster.

It is similar to the index at the back of a book:

```text
without index -> scan many pages
with index    -> jump closer to the answer
```

Indexes help reads, but they also use storage and make writes slightly more
expensive. Add indexes for common lookups, not every column.

## Indexes Added

File:

```text
dictionary/models.py
```

### Owner And Word

```python
models.Index(fields=["owner", "word"], name="word_owner_word_idx")
```

Our main words page always filters by the logged-in owner and sorts by word.
This index supports that common pattern:

```text
WHERE owner = current_user
ORDER BY word
```

It also helps us look up a user's words efficiently as the dictionary grows.

### Newest Words

```python
models.Index(fields=["-created_at"], name="word_created_idx")
```

The staff dashboard asks for the newest words:

```python
Word.objects.order_by("-created_at")
```

This index helps that recent-words query.

## What Is `select_related`?

Suppose a `Word` has a `Category`.

This code fetches words first:

```python
words = Word.objects.all()
```

Then this template accesses a category:

```django
{{ entry.category }}
```

Without preparation, Django may perform another database query for each
category. That pattern is called an **N+1 query problem**:

```text
1 query for the words
+ one query for each category
```

We changed the words page to:

```python
words = Word.objects.select_related("category").filter(
    owner=request.user
)
```

`select_related` joins the related ForeignKey row in the same query.

```text
1 query for words and categories
```

Use it for one-to-one and ForeignKey relationships.

## `prefetch_related`

`select_related` is for one related object, such as:

```text
Word -> Category
```

`prefetch_related` is useful for collections, such as:

```text
Category -> many Words
User -> many Words
```

It usually runs separate efficient queries and combines the results in
Python.

We do not need it in this small page yet, but it is the next tool to remember.

## Search And Indexes

Our search uses:

```python
icontains
```

across `word`, `meaning`, and `example`.

The simple B-tree indexes added in this lesson are excellent for owner
filtering and ordering, but they do not automatically make every
`icontains` search fast.

For a small personal dictionary, this is perfectly fine. Later, if the
dictionary becomes large, we can study PostgreSQL full-text search or
specialized search indexes.

## The Migration

Changing `models.py` does not change the database immediately.

Create a migration:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py makemigrations dictionary
```

Apply it locally:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py migrate
```

When the migration is committed, Render's `build.sh` applies the same
migration to Neon during deployment.

## Neon Connection Note

Neon may pause idle compute and close idle SSL connections. For this small
Render deployment, the project uses:

```text
DATABASE_CONN_MAX_AGE=0
```

That tells Django to close the database connection after each request. It
avoids reusing a stale connection when Neon wakes up. Django also enables
connection health checks for the external PostgreSQL configuration.

## Safer Query Habits

### Filter At The Database

Prefer:

```python
Word.objects.filter(owner=request.user)
```

Avoid loading every word and filtering in Python:

```python
all_words = list(Word.objects.all())
my_words = [word for word in all_words if word.owner == request.user]
```

The first version lets the database do the filtering.

### Select Only What You Need

For very large tables, `values()` or `only()` can reduce selected columns.
Do not use them automatically; they can make code less readable and cause
extra queries if a missing field is accessed later.

### Paginate Large Lists

The words page already uses Django's `Paginator`, so it does not render every
word on one screen.

## How To Verify

Run the normal checks:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py check
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py makemigrations --check --dry-run
```

To inspect SQL while learning, use Django's QuerySet:

```python
print(words.query)
```

Do not print sensitive connection strings. A QuerySet is lazy: Django builds
the SQL first and runs it when the data is actually needed.

## Main Memory Hook

```text
filter in the database
index common lookups
select_related ForeignKeys
prefetch collections
paginate large lists
measure before optimizing
```

## Next Lesson

Next: caching basics and when caching is actually useful.
