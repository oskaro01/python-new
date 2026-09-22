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

`request` is the browser request. The template path tells Django which HTML
file to use. `context` is a dictionary of values available in that template:
for example, `context["heading"]` appears as `{{ heading }}`. A template can
also loop over a list using `{% for item in lesson_points %}`.

## Template Inheritance

`base.html` is the shared page shell.

`home.html` and `about.html` reuse it with:

```django
{% extends "pages/base.html" %}
```

This keeps repeated HTML in one place.

`{% block content %}` in `base.html` marks the area each child page fills.
The `pages/` subfolder inside `templates/` keeps template names distinct if
another app later has its own `home.html`.

## Key Memory Hook

```text
views.py prepares data
template displays data
base.html avoids repeated layout
```

## Next Lesson

Lesson 05 moves CSS into a static file. Lesson 06 then adds a word form.
