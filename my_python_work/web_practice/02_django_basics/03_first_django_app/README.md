# Django Basics 03: First Django App

This lesson adds the first Django app to the tiny project from lesson 02.

## Big Idea

```text
Django project = whole website configuration
Django app = one feature area inside the website
```

For us:

```text
project: mini_site
app: pages
```

The project keeps settings and the top-level URL map.

The app keeps feature code like views and app-specific URLs.

## Files Added Or Changed

```text
02_first_django_project/
    mini_site/
        settings.py      # registers the pages app
        urls.py          # sends page URLs to pages.urls
    pages/
        __init__.py
        apps.py
        urls.py
        views.py
```

## Run

From the project root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/about/
```

Stop it with `Ctrl+C`.

## Check Without Starting Server

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check
```

## What Changed

Before:

```text
mini_site/urls.py had the home view directly.
```

Now:

```text
mini_site/urls.py includes pages.urls
pages/urls.py connects URLs to pages/views.py
```

## Key Memory Hook

```text
Project routes big sections.
Apps handle their own feature URLs.
```

## Next Lesson

Next we will add static files so CSS can live outside the HTML.
