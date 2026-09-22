# Django Basics 05: Static Files

Templates give us HTML.

Static files give us CSS, images, and JavaScript.

In this lesson, we move CSS out of `base.html` and into a real static file.

## Big Idea

```text
Template = HTML structure
Static file = CSS/image/JavaScript asset
```

## Files Added Or Changed

```text
02_first_django_project/
    pages/
        templates/
            pages/
                base.html
        static/
            pages/
                styles.css
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

Check that Django can find the CSS file:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py findstatic pages/styles.css
```

## Visual Proof

The original lesson showed a temporary CSS-loaded label on every page. We
removed that label when the dictionary received its finished layout. To
verify static files now, run `findstatic` above, then open a page and check
that the header and form styles appear. In browser Developer Tools, the
Network tab should show `/static/pages/styles.css` with status 200.

## What Changed

Before, `base.html` had CSS inside a `<style>` tag.

Now `base.html` loads CSS with:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'pages/styles.css' %}">
```

## Why Static Folders Repeat The App Name

The path is:

```text
pages/static/pages/styles.css
```

That looks repetitive, but it prevents name conflicts later.

For example, two apps could both have a `styles.css` file. The extra `pages/` folder keeps this app's CSS clearly named.

## Key Memory Hook

```text
HTML goes in templates/
CSS goes in static/
{% static %} builds the asset URL
```

## Next Lesson

Lesson 06 introduces the New Word form. The database model comes in lesson 07.
