# Django Basics 15: Django Admin

Django admin is a ready-made interface for managing database rows. Our Word
model was registered in lesson 07; now you can use that registration.

## What Is Already Wired Up

- `mini_site/urls.py` sends `/admin/` to Django's admin site.
- `settings.py` enables Django's admin, authentication, and sessions apps.
- `dictionary/admin.py` registers `Word` with `@admin.register(Word)`.
- `Word.__str__()` in `dictionary/models.py` gives entries readable names.

`WordAdmin` changes how the admin list works:

- `list_display`: columns for word, category, favorite status, and created time.
- `list_filter`: filters for category and favorite status.
- `search_fields`: searches word, meaning, example, and category.
- `ordering`: sorts the list by word.

These settings affect `/admin/`. They do not change the public `/words/`
search page. Both pages read and write the same SQLite Word table.

## Try It

From the repository root, ensure the built-in tables exist:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py migrate
```

Create an admin account. Django asks for a username and password in your
terminal; the password is not written into our code:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py createsuperuser
```

Start the server:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Open `http://127.0.0.1:8000/admin/`, sign in, and open **Words**. Try search,
filters, and editing a test word. Return to `/words/` to see the same change.
Stop the server with `Ctrl+C`.

Use an account you create locally; do not put its password in a README or
commit it. The SQLite file is ignored by Git. If you already created a
superuser, use it instead of running `createsuperuser` again.

## Key Memory Hook

```text
Word model -> registered in admin.py -> /admin/ manages Word rows
```

## Next Lesson

Next: user accounts and which words each user is allowed to change.
