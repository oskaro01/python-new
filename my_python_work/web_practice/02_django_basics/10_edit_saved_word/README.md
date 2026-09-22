# Django Basics 10: Edit A Saved Word

Lesson 09 opened one saved word by ID. Now that page has an **Edit word**
link. The edit page reuses `WordForm` from the add page.

## Follow One Edit

1. Open `/words/` and click a saved word.
2. Click **Edit word**. The URL is `/words/<ID>/edit/`.
3. The view finds that Word row with `get_object_or_404(Word, pk=word_id)`.
4. On a GET request, `WordForm(initial={...})` fills the fields with the
   word's current values. `initial` only controls what appears in the form;
   it does not change the database.
5. On a POST request, `WordForm(request.POST)` checks the new values.
6. If valid, the view copies `form.cleaned_data` onto the existing Word,
   calls `word.save()`, and redirects to its detail page.
7. If invalid, the form and its errors appear again. The old database row
   remains unchanged.

The loop uses `setattr(word, field, value)` to set a named attribute. For
example, `setattr(word, "meaning", "calm")` is equivalent to
`word.meaning = "calm"`. Only the four fields defined in `WordForm` are
updated, so `is_favorite` and the timestamps are not copied from the form.
When `save()` runs, Django updates `updated_at` automatically.

The same `word_form.html` template works for adding and editing because both
views pass it a `form`, `heading`, and `message`.

## Try It

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Open `http://127.0.0.1:8000/words/`, click a word, edit its meaning, and
save. Refresh the detail page: the change should still be there. Try changing
the word to one character; the error should appear and the saved word should
stay unchanged. Stop the server with `Ctrl+C`.

This lesson changes no model fields, so it needs no new migration.

## Files Changed

- `pages/urls.py`: route `/words/<ID>/edit/`.
- `pages/views.py`: load, validate, update, and save one Word.
- `pages/templates/pages/word_detail.html`: link to the edit page.

## Key Memory Hook

```text
GET -> initial values -> form
POST -> validate -> change existing object -> save() -> detail page
```

## Next Lesson

Next: delete a saved word with a confirmation page.
