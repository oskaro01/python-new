# Django Basics 28: Production Maintenance

This lesson adds two practical production habits:

```text
friendly error pages
useful deployment logs
```

When the app is live, users should not see raw technical errors. You also
need logs so you can understand what happened after a request fails.

## What We Added

### Custom 404 Page

File:

```text
pages/templates/pages/404.html
```

Django shows this when a URL does not match any route.

Example:

```text
/this-page-does-not-exist/
```

### Custom 500 Page

File:

```text
pages/templates/pages/500.html
```

Django shows this when the server crashes while handling a request.

Users see a calm page. Developers check logs.

### Error Handlers

File:

```text
mini_site/urls.py
```

We added:

```python
handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"
```

These tell Django which view should render each error page.

### Error Views

File:

```text
pages/views.py
```

The 404 view receives:

```text
request
exception
```

The 500 view receives:

```text
request
```

Both return normal HTML with a special status code.

## Logging

File:

```text
mini_site/settings.py
```

We added console logging for:

```text
django.request
pages
```

On Render, console logs appear in the service logs.

That means when a bad URL or server error happens, you can open Render logs
and see useful messages.

## Important Debug Rule

Custom 404 and 500 pages are mainly visible when:

```text
DEBUG=False
```

Locally, while `DEBUG=True`, Django often shows its helpful developer pages
instead.

That is good while coding. In production, users should get the calm custom
pages.

## Status Codes

The page content and the HTTP status are different things:

| Page | Meaning | Status |
| --- | --- | --- |
| `404.html` | URL not found | `404` |
| `500.html` | Server crashed | `500` |

The browser shows the HTML. Search engines and monitoring tools read the
status code.

## How To Verify

Local lightweight check:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py check
```

After deploying, visit a wrong URL:

```text
https://your-render-url.onrender.com/not-real/
```

You should see the custom 404 page.

Then check Render logs. You should see a warning for the missing page.

## Why This Matters

Production apps need:

- clean user-facing error pages
- logs for debugging
- no secret details shown to users
- predictable HTTP status codes

This is one of the first steps from "it works locally" to "it is maintainable
online."

## Next Lesson

Next: database performance basics, indexes, and safer query habits.
