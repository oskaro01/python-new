# Django Basics 08: Save Words To The Database

Lesson 07 described the Word table. This lesson uses it: the New Word form
saves an entry, and the Words page reads saved entries back.

## First: Create The Database Tables

From the repository root, run this once:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py migrate
```

`migrate` applies the migration from lesson 07 to SQLite. The database file
is created beside `manage.py`. It is ignored by Git. You do not need to run
`makemigrations` again because `0001_initial.py` already exists.

## Follow A Save

1. Open `/words/new/`. Django makes an empty `WordForm` for a GET request.
2. Submit the form. The browser sends a POST request with your typed values.
3. `WordForm(request.POST)` checks the values with `form.is_valid()`.
4. On success, `form.cleaned_data` contains the four form fields. The view
   passes them to `Word.objects.create(**form.cleaned_data)`.
5. `create()` inserts one row in the Word table and the view redirects to
   `/words/`. A redirect makes refreshing the list safe from a repeat POST.
6. The list view calls `Word.objects.all()`. This is a QuerySet: a database
   query for all saved Word objects. The template loops through them.

`**form.cleaned_data` unpacks a dictionary into named arguments. For example,
`{"word": "serene", "meaning": "calm"}` becomes
`Word.objects.create(word="serene", meaning="calm")`. The optional fields are
included too. The model fills in `is_favorite` and the timestamps itself.

If validation fails, the view shows the same form with errors. It does not
create a row. `{{ entry.word }}` in the list template displays a saved model
field; Django escapes it for HTML.

## Try It

After `migrate`, start Django:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Open `http://127.0.0.1:8000/words/new/`, save a word, and look for it at
`http://127.0.0.1:8000/words/`. Stop the server with `Ctrl+C`.

Try a one-character word too. It should show an error and should not appear
in the list. Restarting the server should leave valid saved words in place.

## Files Changed

- `pages/views.py`: save valid form data and query saved words.
- `pages/urls.py`: add `/words/`.
- `pages/templates/pages/word_form.html`: save button.
- `pages/templates/pages/word_list.html`: show saved words or an empty state.
- `pages/templates/pages/base.html`: add a Words navigation link.

## Key Memory Hook

```text
form -> is_valid() -> cleaned_data -> Word.objects.create() -> SQLite
SQLite -> Word.objects.all() -> template -> browser
```

## Next Lesson

Next we can give each saved word its own page, then add editing and deleting.
