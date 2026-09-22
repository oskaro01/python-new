# Django Basics 06: Forms

Now we start the dictionary direction.

This lesson adds a simple "new word" form.

It does not save to the database yet. First we learn how Django receives and validates form data.

## Big Idea

```text
HTML form sends data
request.POST receives data
Django Form validates data
cleaned_data gives safe Python values
```

## Files Added Or Changed

```text
02_first_django_project/
    pages/
        forms.py
        urls.py
        views.py
        templates/
            pages/
                base.html
                word_form.html
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
http://127.0.0.1:8000/words/new/
```

## Check Without Starting Server

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check
```

## What This Teaches

- `forms.Form`
- text fields
- optional fields
- `request.method`
- `request.POST`
- `form.is_valid()`
- `form.cleaned_data`
- CSRF token
- showing form errors

## Why We Use CSRF

Django forms that use `POST` should include:

```django
{% csrf_token %}
```

This helps Django reject fake form submissions from another site.

## Key Memory Hook

```text
request.POST = raw submitted text
form.is_valid() = check it
form.cleaned_data = trusted Python values
```

## Next Lesson

Next we will add a database model for dictionary words.

