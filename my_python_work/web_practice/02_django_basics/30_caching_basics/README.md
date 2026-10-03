# Django Basics 30: Caching Basics

Caching means saving a result for a short time so the app does not have to
repeat the same work on every request.

This lesson adds a safe, small cache:

```text
staff dashboard summary numbers
```

We do not cache private word pages yet.

## Why Not Cache Every Page?

Our base template changes depending on the user:

```text
logged out -> Log in / Register
logged in  -> Account / username / Log out
```

If we cached full HTML carelessly, one user could see another user's header or
old private data. So we start with a safer pattern:

```text
cache small data
render the page normally
clear the cache when the data changes
```

## Cache Backend

File:

```text
mini_site/settings.py
```

We configured Django's local-memory cache:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "personal-dictionary-cache",
    }
}
```

This cache lives inside the running Python process.

That means:

- it is fast
- it is simple
- it disappears when the server restarts
- it is fine for learning and small temporary data

For larger production systems, people often use Redis or Memcached.

## What We Cached

File:

```text
pages/views.py
```

The staff dashboard shows several count numbers:

```text
total words
total categories
total users
users with words
orphan words
```

Those numbers are safe to cache for staff users because they are not one
specific user's private dictionary page.

The cache key is:

```python
STAFF_DASHBOARD_STATS_CACHE_KEY = "staff-dashboard-stats"
```

The timeout is:

```python
STAFF_DASHBOARD_STATS_TIMEOUT = 60
```

That means Django can reuse the same stats for up to 60 seconds.

## Cache Flow

The view uses this idea:

```text
1. Ask cache for dashboard stats.
2. If found, reuse them.
3. If missing, query the database.
4. Save the result in cache for 60 seconds.
5. Render the page normally.
```

This is called a **cache miss** when the value is missing and a **cache hit**
when the value exists.

## Cache Invalidation

Invalidation means clearing cached data when it may be outdated.

We clear the staff dashboard stats cache when:

```text
a word is created
a word is imported
a word is edited
a word is deleted
```

The helper function is:

```python
def clear_staff_dashboard_cache():
    cache.delete(STAFF_DASHBOARD_STATS_CACHE_KEY)
```

This is the most important caching lesson:

```text
caching is easy
knowing when to clear the cache is the real work
```

## What We Did Not Cache

We did not cache:

```text
word list pages
word detail pages
login pages
registration pages
import/export responses
```

Those pages are user-specific, security-sensitive, or change often.

## Local Vs Render

The local-memory cache is separate per running process.

On your laptop:

```text
stop server -> cache gone
start server -> empty cache
```

On Render:

```text
service restarts -> cache gone
new deploy -> cache gone
```

That is okay for temporary dashboard stats.

## When Caching Helps

Caching is useful when:

- the same data is requested often
- calculating the data costs database work
- a tiny bit of staleness is acceptable
- you know how to clear the cache

Caching is risky when:

- the page is private per user
- the data changes constantly
- stale data would confuse people
- secrets or personal data might leak

## How To Verify

Run:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py check
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py test pages
```

Manual check:

1. Log in as a staff user.
2. Open `/staff/`.
3. Add a word.
4. Open `/staff/` again.

The dashboard should still show correct counts because the cache is cleared
when words change.

## Main Memory Hook

```text
cache reusable data
avoid caching private HTML
set a timeout
clear cache when data changes
use Redis later for serious shared caching
```

## Next Lesson

Next: email provider setup for real password reset emails.
