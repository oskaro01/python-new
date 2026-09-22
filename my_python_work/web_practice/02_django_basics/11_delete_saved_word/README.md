# Django Basics 11: Delete A Saved Word

You can now remove a saved dictionary word from its detail page. Deleting is
permanent for that row, so the app asks you to confirm first.

## Follow One Delete

1. On a word detail page, click **Delete word**.
2. The browser sends `GET /words/<ID>/delete/`. Django finds the Word by ID
   and shows a confirmation page. No data changes on this request.
3. Press **Delete word** on that page. Its form sends a POST request to the
   same URL, with a CSRF token.
4. The view calls `word.delete()` and redirects to `/words/`.
5. The deleted word no longer appears in the list. Its old detail URL now
   returns a 404 because that row no longer exists.

**Cancel** goes back to the word detail page without submitting the form.
`get_object_or_404(Word, pk=word_id)` handles an ID that does not exist.

The important rule: a GET request only displays the confirmation page;
the POST request performs the deletion. This prevents a normal link open or
page preview from deleting data.

## Try It

Start Django from the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Open `http://127.0.0.1:8000/words/`, choose a word, and test **Cancel**
first. Then delete a test word and check that it disappears from the list.
Stop the server with `Ctrl+C`.

Use a test word for this lesson. Deleting a row does not have an undo button.
No model fields changed, so no new migration is needed.

## Files Changed

- `pages/urls.py`: route `/words/<ID>/delete/`.
- `pages/views.py`: display confirmation on GET; delete on POST.
- `pages/templates/pages/word_detail.html`: delete link.
- `pages/templates/pages/word_confirm_delete.html`: confirmation form.

## Key Memory Hook

```text
GET -> show confirmation
POST -> delete row -> redirect to list
```

## Next Lesson

Next: search and filter the saved words.
