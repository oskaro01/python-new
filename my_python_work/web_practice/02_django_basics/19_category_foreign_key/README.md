# Django Basics 19: Category ForeignKey

Categories are now real database objects instead of repeated text stored on
every Word. One Category can be connected to many Words.

## First: Apply The Migration

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py migrate
```

Migration `0003_category_model.py` creates the Category table and converts
existing category text into Category rows. Your existing category names are
preserved.

## Before And After

Before, each Word stored its own category text:

```text
serene -> "adjective"
stern  -> "adjective"
```

Now the database stores one Category and both words point to it:

```text
Category: adjective
        ^          ^
     serene      stern
```

That is a one-to-many relationship:

```text
one Category -> many Words
one Word -> zero or one Category
```

## The ForeignKey

`Word.category` is a `ForeignKey` to `Category`. SQLite stores the category's
ID in the Word row. Django lets us work with the object itself:

```python
word.category.name
category.words.all()
```

`related_name="words"` creates the second query. `on_delete=models.SET_NULL`
means deleting a Category keeps its Words and clears their category.

Each Category also has an owner. The unique constraint prevents one user from
having two categories with exactly the same name.

## Keeping The Form Simple

The form still shows a normal Category text input. `category_name` is a form
field rather than a Word model field. During `save()` the form:

1. Reads and trims the category name.
2. Searches that user's categories without caring about letter case.
3. Reuses the matching Category or creates it once.
4. Connects the Word to that Category.

This keeps the interface easy while the database uses a proper relationship.
Leaving Category empty sets `word.category` to `None`.

## What The Data Migration Does

The migration performs four safe steps:

1. Temporarily renames the old text field to `category_text`.
2. Creates the Category table and the new ForeignKey.
3. Creates or reuses Category rows and connects existing Words.
4. Removes the temporary text field after conversion.

This is called a **data migration** because it moves existing values, not just
the table structure.

## Try It

After `migrate`, run the server and create two words using the same category.
Open `/admin/` and inspect Categories: you should see one Category connected
to both words. Edit one word and change or remove its category.

## Files Added Or Changed

- `dictionary/models.py`: Category model and Word ForeignKey.
- `dictionary/migrations/0003_category_model.py`: structure and data conversion.
- `dictionary/admin.py`: Category management and relationship search.
- `pages/forms.py`: accept category text and reuse/create Category objects.
- `pages/views.py`: give WordForm the current user.
- `pages/templates/pages/word_form.html`: render `category_name`.

## Key Memory Hook

```text
repeated category text -> one Category row <- many Word rows
```

## Next Lesson

Next: Password reset with Django's built-in authentication views.
