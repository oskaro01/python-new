# Django Basics 14: Django Messages

After saving, editing, or deleting a word, the app now shows a short success
message on the next page.

## Follow One Message

1. Submit a valid New Word form.
2. The view saves the Word, then calls
   `messages.success(request, "Word saved.")`.
3. The view redirects to `/words/`.
4. `base.html` loops over `messages` and displays the message above the page.
5. After it is displayed, Django consumes it; refreshing does not create a
   second message.

The same pattern says **Word updated.** after editing and **Word deleted.**
after deletion. Form validation errors stay next to the form fields; they are
different from these one-time success messages.

Django already had `django.contrib.messages`, its middleware, and its template
context processor in `mini_site/settings.py`. The middleware carries messages
across the redirect; the context processor makes `messages` available in the
template. `aria-live="polite"` helps screen readers announce the result.

## Try It

Start Django from the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Save a test word, edit it, then delete it. Check the message after each
action. Refresh after one action; the message should disappear. Stop the
server with `Ctrl+C`.

This lesson changes no model fields, so no migration is needed.

## Files Changed

- `pages/views.py`: queue a success message after each database change.
- `pages/templates/pages/base.html`: show queued messages on every page.
- `pages/static/pages/styles.css`: style the message.

## Key Memory Hook

```text
change data -> queue message -> redirect -> show message once
```

## Next Lesson

Next: learn Django admin so you can inspect and manage saved words there.
