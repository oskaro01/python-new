# Django Basics 09: Word Detail And 404

Each saved word now has its own page. Click a word on `/words/` to open it.

## How The URL Finds One Word

Suppose a saved Word row has ID `3`:

```text
/words/3/ -> pages/urls.py -> word_detail(request, word_id=3)
          -> Word row with primary key 3 -> word_detail.html
```

`<int:word_id>` in `pages/urls.py` accepts an integer from the URL and passes
it to the view. `entry.pk` in `word_list.html` is the row's primary key (ID).
The `{% url %}` tag builds the link from the route name and that ID. The ID
is assigned by the database when the word is saved.

The view uses `get_object_or_404(Word, pk=word_id)`. It asks the database for
one Word with that primary key. If none exists, Django shows a 404 response
instead of crashing. The template displays the returned Word object.

Optional fields only appear when they have values. The Back to words link
returns to the list. Django escapes the displayed text for HTML.

## Try It

Start the server from the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Open `http://127.0.0.1:8000/words/` and click a saved word. You can also
try a nonexistent ID such as `http://127.0.0.1:8000/words/999999/` to see
the 404. Stop the server with `Ctrl+C`.

If you have no saved words yet, first run `migrate` and save one using lesson
08. This lesson adds no model fields, so it needs no new migration.

## Files Changed

- `pages/urls.py`: add the integer ID route.
- `pages/views.py`: fetch one Word or return 404.
- `pages/templates/pages/word_list.html`: link each word to its page.
- `pages/templates/pages/word_detail.html`: display the selected word.

## Key Memory Hook

```text
list link -> ID in URL -> database lookup -> one word or 404
```

## Next Lesson

Next: edit a saved word using a form that starts with its current values.
