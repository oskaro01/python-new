# Django Basics 04: Templates

So far our Django views returned plain text with `HttpResponse`.

Now the `pages` app returns HTML files using Django templates.

## Big Idea

```text
View = Python function
Template = HTML file
Context = data sent from Python to HTML
```

## Files Added Or Changed

```text
02_first_django_project/
    pages/
        views.py
        templates/
            pages/
                base.html
                home.html
                about.html
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

## Check Without Starting Server

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check
```

## What Changed

Before:

```python
return HttpResponse("Hello")
```

Now:

```python
return render(request, "pages/home.html", context)
```

## Template Inheritance

`base.html` is the shared page shell.

`home.html` and `about.html` reuse it with:

```django
{% extends "pages/base.html" %}
```

This keeps repeated HTML in one place.

## Key Memory Hook

```text
views.py prepares data
template displays data
base.html avoids repeated layout
```

## Next Lesson

Next we will add static files so CSS can live outside the HTML.

