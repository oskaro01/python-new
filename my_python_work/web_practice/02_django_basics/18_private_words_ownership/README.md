# Django Basics 18: Private Words And Ownership

Every new Word now belongs to the user who created it. Logged-in users can
list, open, edit, and delete only their own words.

## First: Apply The Migration

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py migrate
```

Migration `0002_word_owner.py` adds an `owner_id` column to the Word table.
Run this before opening the word pages.

## The Relationship

`Word.owner` is a `ForeignKey` to Django's User model:

```text
one User -> many Words
one Word -> one owner
```

`related_name="words"` also allows `user.words.all()` to find that user's
words. `on_delete=models.CASCADE` means deleting a user also deletes their
words.

The owner field is temporarily nullable so the migration preserves words
created before accounts existed. Those older words have no owner, so they do
not appear on anyone's public Words page. An admin can assign their owner at
`/admin/`. New words always receive the logged-in user.

## Saving An Owner

The owner is not included in `WordForm`, because a visitor must never choose
another user as the owner. The view sets it safely:

```python
word = form.save(commit=False)
word.owner = request.user
word.save()
```

`commit=False` creates the Python Word object without inserting it yet. After
the view supplies its owner, `word.save()` inserts the complete row.

## Privacy In Queries

The list starts with:

```python
Word.objects.filter(owner=request.user)
```

Detail, edit, and delete use both the ID and owner:

```python
get_object_or_404(Word, pk=word_id, owner=request.user)
```

Even if one user guesses another user's word ID, the query finds nothing and
returns 404. Hiding links alone would not provide this protection.

`@login_required` protects every word view. A logged-out visitor is redirected
to `/accounts/login/`, then returned to the requested page after login.

## Try It

After `migrate`, run the server:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

1. Log in and create a word.
2. Log out and confirm `/words/` asks you to log in.
3. Create a second account and confirm it cannot see the first account's word.
4. In `/admin/`, assign any older ownerless words to the account you want.

Stop the server with `Ctrl+C`.

## Files Added Or Changed

- `dictionary/models.py`: add the User-to-Word relationship.
- `dictionary/migrations/0002_word_owner.py`: add `owner_id` to SQLite.
- `dictionary/admin.py`: display, search, and filter by owner.
- `pages/views.py`: require login and restrict every Word query by owner.

## Key Memory Hook

```text
request.user owns new Word
every Word query includes owner=request.user
```

## Next Lesson

Next: relationships beyond ownership, using categories or tags as real models.
