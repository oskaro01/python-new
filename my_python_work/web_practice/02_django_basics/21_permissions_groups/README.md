# Django Basics 21: Permissions And Groups

Login answers:

```text
Who are you?
```

Permissions answer:

```text
What are you allowed to do?
```

## What We Added

- A custom `view_all_words` permission on the `Word` model.
- A staff dashboard at `/staff/`.
- A permission-protected view using `permission_required`.
- A navigation link that appears only for users with the permission.
- A 403 response for logged-in users without the permission.

## Apply The Migration

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py migrate
```

The migration creates the custom permission in Django's permission table.

## How Migrations Work

Migrations are Django's saved instructions for changing the database.

```text
models.py        = what we want
migration file   = written instructions
database         = what currently exists
migrate          = execute the instructions
```

Our migration history now looks like this:

```text
0001_initial.py
    creates the first Word table

0002_word_owner.py
    adds ownership to Word

0003_category_model.py
    creates Category and connects it to Word

0004_alter_word_options.py
    adds the custom view_all_words permission
```

There are two main commands:

```powershell
python manage.py makemigrations
```

This compares `models.py` with the previous migration state and writes a new
migration file. It does not change the database yet.

```powershell
python manage.py migrate
```

This executes every migration that has not been applied. Django records
completed migrations in its `django_migrations` table.

To see the status:

```powershell
python manage.py showmigrations dictionary
```

The symbols mean:

```text
[X] 0003_category_model
    this migration has already run

[ ] 0004_alter_word_options
    the file exists, but it has not run yet
```

That is why the custom permission was missing until we ran `migrate`.
Migrations are not empty placeholders. They let Django update the database
without deleting existing words.

## Give A User The Permission

1. Log in to `/admin/` as a superuser.
2. Open **Groups** and create `Dictionary Managers`.
3. Add the permission **Dictionary | word | Can view all dictionary words**.
4. Open a user and add that user to the group.
5. Log in as that user and open `/staff/`.

The user does not need to be a superuser. The group grants only this specific
permission.

## Important Difference

```text
is_authenticated -> the user is logged in
is_staff         -> the user may enter Django Admin
has permission   -> the user may perform one protected action
is_superuser     -> bypasses permission checks
```

The dashboard uses the permission, not a username check:

```python
@permission_required("dictionary.view_all_words", raise_exception=True)
```

That keeps the rule reusable and easy to change in the Admin.

## Files

- `dictionary/models.py`: declares the custom permission.
- `dictionary/migrations/0004_alter_word_options.py`: creates it in the database.
- `pages/views.py`: protects and builds the staff dashboard.
- `pages/templates/pages/staff_dashboard.html`: displays all words.
- `pages/templates/pages/base.html`: shows the Staff link only when allowed.

## Key Memory Hook

```text
user -> group -> permission -> protected view
```

## Next Lesson

Next: account/profile information and practical dictionary data workflows.
