# Django Basics 16: ModelForm

We already learned to validate a form, create a Word, and edit a saved Word.
Now Django can connect those steps for us with `forms.ModelForm`.

## What Changed

`WordForm` now declares `model = Word` and lists the four fields users may
edit. Django builds those fields from `Word` in `dictionary/models.py`.
`help_texts` and `widgets` keep our labels, hints, and input sizes familiar.
We still use `clean_word()` to reject words shorter than two characters.

The explicit `fields` list matters: `is_favorite` and the timestamps are not
editable through this public form.

## Add Versus Edit

```python
# Add a new row after validation:
form = WordForm(request.POST)
if form.is_valid():
    form.save()

# Update one existing row after validation:
form = WordForm(request.POST, instance=word)
if form.is_valid():
    form.save()
```

On an edit GET request, `WordForm(instance=word)` fills the inputs from that
saved row. On an edit POST request, `instance=word` tells `save()` to update
that row instead of creating another one. Without `instance`, `save()` would
make a new Word.

`is_valid()` still runs field and custom validation before saving. An invalid
form displays errors and does not save. The view still redirects after a
successful save, so refreshing the next page will not repeat the POST.

## Try It

Start Django from the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Add a test word, then edit its meaning. Confirm there is still one row for
that word. Try a one-character word to see `clean_word()` reject it. Stop the
server with `Ctrl+C`.

No model fields changed, so no new migration is needed.

## Files Changed

- `pages/forms.py`: define `WordForm` from the `Word` model.
- `pages/views.py`: call `form.save()` for add and edit.

## Key Memory Hook

```text
ModelForm + POST -> validate -> save()
ModelForm + instance -> edit an existing row
```

## Next Lesson

Next: user accounts and permissions, so each person's words can be private.
