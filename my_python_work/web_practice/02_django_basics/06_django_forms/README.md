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

## Follow One Form Visit

1. You open `/words/new/`. The browser sends a `GET` request.
2. `pages/urls.py` calls `new_word(request)` in `pages/views.py`.
3. The view creates an empty `WordForm()` and renders `word_form.html`.
4. You enter a word and press **Check word**. The browser sends a `POST`
   request containing the form values.
5. The view builds `WordForm(request.POST)` and calls `form.is_valid()`.
6. If valid, the view passes `form.cleaned_data` to the template, which shows
   the submitted values. Nothing is saved to the database in this lesson.
7. If invalid, the same form is shown again with errors beside its fields.

`GET` asks for the form; `POST` submits it. The `method="post"` attribute in
`word_form.html` chooses the second request type.

## Inside WordForm

`forms.py` defines the fields. `word` is required by default; `meaning`,
`example`, and `category` use `required=False`. `max_length` limits the number
of characters. A `widget` chooses the HTML input type and can set a
placeholder or textarea size.

The `clean_word()` method runs during `form.is_valid()`. It strips surrounding
spaces, rejects words shorter than two characters, and returns the cleaned
word. Raising `forms.ValidationError` attaches the message to the word field.
For example, entering ` a ` becomes `a` and fails the two-character check.

The template renders each field with `{{ form.word }}` and its errors with
`{{ form.word.errors }}`. The view keeps the bound form after an invalid POST,
so you can correct it without retyping everything.

## Why We Use CSRF

Django forms that use `POST` should include:

```django
{% csrf_token %}
```

This helps Django reject fake form submissions from another site.

The token appears in the HTML form. Django checks it when the POST arrives.

## Key Memory Hook

```text
request.POST = raw submitted text
form.is_valid() = check it
form.cleaned_data = trusted Python values
```

## Next Lesson

Next we will add a database model for dictionary words.
