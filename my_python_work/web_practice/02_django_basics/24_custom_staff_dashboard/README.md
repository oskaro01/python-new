# Django Basics 24: Custom Staff Dashboard

This lesson turns the protected `/staff/` page into a small analytics dashboard.

## What We Added

- Total words.
- Total categories.
- Total users.
- Users who have saved words.
- Words without an owner.
- Top users by word count.
- Top categories by word count.
- Recent words table.

## Why This Matters

Django Admin is excellent for editing rows. A custom dashboard is better for
answering business questions quickly:

```text
How many words exist?
Who is using the app?
Which categories are growing?
What was added recently?
```

This is similar to ecommerce admin dashboards, but smaller and easier to learn.

## Protection

The dashboard still uses the custom permission from Lesson 21:

```python
@permission_required("dictionary.view_all_words", raise_exception=True)
```

So only users with `dictionary.view_all_words` can open `/staff/`.

## ORM Tools Used

`Count` lets Django count related rows:

```python
User.objects.annotate(word_count=Count("words"))
```

That means:

```text
For each user, count how many Word rows point to that user.
```

`select_related()` helps Django load related owner/category data efficiently:

```python
Word.objects.select_related("owner", "category")
```

That matters when a page shows many rows and each row needs relationship data.

## Files

- `pages/views.py`: dashboard queries and summary counts.
- `pages/templates/pages/staff_dashboard.html`: analytics layout.
- `pages/static/pages/styles.css`: dashboard cards and tables.

## Key Memory Hook

```text
Django Admin edits data.
Custom dashboards explain data.
```

## Next Lesson

Next: testing the important dictionary rules.
