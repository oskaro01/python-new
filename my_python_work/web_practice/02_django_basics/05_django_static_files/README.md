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

`base.html` contains this empty paragraph:

```html
<p class="static-proof"></p>
```

The CSS file fills it with text:

```css
.static-proof::before {
    content: "Static CSS loaded from pages/styles.css";
}
```

If you see that message in the browser, the static CSS file is loading.

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

Next we will add a database model for dictionary words.
