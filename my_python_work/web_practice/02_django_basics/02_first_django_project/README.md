# Django Basics 02: First Django Project

This is our first tiny Django project. Later lessons keep adding to this same
folder, so the files you see now include work from lessons 03-07.

It started intentionally small:

- one `manage.py`
- one project package named `mini_site`
- one first app named `pages`
- simple page routes
- plain text responses at the start

At the end of lesson 02, there were no templates or dictionary model. Those
arrived in later lessons. The current project has both.

## Run

From the project root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

Stop it with `Ctrl+C`.

## Files

```text
02_first_django_project/
    manage.py
    mini_site/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py
    pages/
        apps.py
        urls.py
        views.py
```

## What Each File Means

`manage.py`

- command tool for this Django project
- used for `runserver`, `check`, migrations, creating apps, and more

`settings.py`

- project configuration
- installed apps, database settings, debug mode, secret key, static files

`urls.py`

- route table
- connects a URL path to Python code
- `mini_site/urls.py` delegates page paths to `pages/urls.py`

`pages/views.py`

- contains functions that receive a request and return a response
- later lessons changed those responses from plain text to HTML templates

`asgi.py` and `wsgi.py`

- server entry points
- mostly leave them alone while learning

`pages/`

- first Django app
- holds simple page views and app-specific URLs

## Check Without Starting Server

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check
```

## Key Memory Hook

```text
Browser asks URL
Django checks urls.py
Matching view returns response
```
====
test,

user name = ayzal
pass = 2458
====


## Next Lesson

Lesson 03 introduces the `pages` app and shows how a URL reaches a view.
