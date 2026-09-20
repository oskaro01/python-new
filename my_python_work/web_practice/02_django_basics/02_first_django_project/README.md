# Django Basics 02: First Django Project

This is our first tiny Django project.

It is intentionally small:

- one `manage.py`
- one project package named `mini_site`
- one URL route
- one plain text response

No database models yet. No templates yet. No app folder yet.

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

`asgi.py` and `wsgi.py`

- server entry points
- mostly leave them alone while learning

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

## Next Lesson

Next we will create a Django app, because real Django projects are usually split into apps.

