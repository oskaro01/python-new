# Django Dictionary: Edit, Delete, Import, and Export Flows

The save flow created a word. This document follows what happens when the
user changes an existing word, deletes one, or moves a backup file into the
database. These actions reuse authentication but have different safety rules.

## The shared rule: identify the row and the owner together

The detail, edit, and delete views use this shape:

```python
get_object_or_404(
    Word,
    pk=word_id,
    owner=request.user,
)
```

The primary key alone is not enough. A user may know another user's numeric
ID. Combining `pk` with `owner=request.user` means an outsider receives a
normal 404 and the view never gets an unauthorized object to edit or delete.

## Editing a word

### Opening the edit page

The detail template links to:

```text
GET /words/<word_id>/edit/
```

`pages/urls.py` selects `views.edit_word`. The view first loads the row with
the owner filter. If the row is yours, it creates a bound-to-instance form:

```python
form = WordForm(instance=word, user=request.user)
```

The form reads the current values from the `Word` object. Its custom category
field is initialized from `word.category.name`, because `category_name` is a
human-friendly form field rather than a direct model field.

The same `word_form.html` template is used for creating and editing. The
heading and message change through the context.

### Submitting the edit

The browser sends:

```text
POST /words/17/edit/
word=vivid
meaning=bright and lively
example=The colors were vivid.
category_name=adjective
focus_first=on
csrfmiddlewaretoken=...
```

The view loads the same owner-scoped row again and creates:

```python
WordForm(request.POST, instance=word, user=request.user)
```

`instance=word` is the important difference from creating. A valid save
updates that row instead of inserting a new one.

The form repeats validation. Its custom `save()` method resolves the category:

```text
same owner + same category name -> reuse category
new category name              -> create owner-scoped category
blank category                 -> set category to NULL
```

Then Django writes an SQL `UPDATE` for the word. `updated_at` changes while
`created_at` remains the original creation time.

After success, the view clears staff statistics, adds a message, and redirects
to the word detail page:

```text
POST edit -> UPDATE row -> 302 -> GET /words/17/ -> render detail
```

This is still POST/Redirect/GET, so refreshing the detail page does not repeat
the edit.

## Deleting a word

### The first request only confirms

The detail page's Delete link goes to:

```text
GET /words/<word_id>/delete/
```

The view authenticates the user, loads the owner-scoped row, and renders
`word_confirm_delete.html`. It does not delete anything during this GET.

This two-step design prevents a link preview, browser prefetch, or accidental
GET request from destroying data.

### The confirmation form performs the mutation

The confirmation template contains a CSRF-protected POST form. When the user
confirms, the browser sends:

```text
POST /words/17/delete/
csrfmiddlewaretoken=...
```

The view retrieves the owner-scoped row and calls:

```python
word.delete()
```

Django sends a SQL `DELETE`. The category is not automatically deleted because
the word's foreign key uses `on_delete=models.SET_NULL`; the category can be
reused by other words.

The view clears staff statistics, adds a success message, and redirects to the
owner's word list. A repeated POST for the same ID finds no owner-scoped row
and returns 404.

```text
GET confirmation -> render only
POST confirmation -> DELETE row -> 302 -> GET /words/
```

## Bulk actions

The Manage page submits selected word IDs to:

```text
POST /words/bulk-action/
```

The view gets the selected IDs from `request.POST.getlist("selected_words")`
and then applies this owner filter:

```python
Word.objects.filter(owner=request.user, pk__in=selected_ids)
```

If the submitted list contains another user's ID, that row is not in the
QuerySet. The current user can focus or delete only rows that pass both
conditions.

The selected action is one of:

```text
focus   -> UPDATE focus_first = true
unfocus -> UPDATE focus_first = false
delete  -> DELETE matching rows
```

An empty selection creates an informational message and performs no mutation.
An unknown action creates an error message instead of guessing.

## Export flow

The list page links to two GET endpoints:

```text
GET /words/export/csv/
GET /words/export/json/
```

Both views require login and filter by the current owner before creating the
file. The export cannot include another user's private words.

The helper `word_rows()` converts model objects to this portable shape:

```text
word, meaning, example, category, focus_first
```

The CSV helper streams a CSV response. The JSON helper serializes a list of
objects with UTF-8 text preserved. `Content-Disposition` tells the browser to
download the result as a file. Export is read-only; it does not change the
database.

## Import flow

### The upload request

The Import page uses:

```html
<form method="post" enctype="multipart/form-data">
```

`multipart/form-data` is required because the request contains file bytes. The
view constructs:

```python
ImportWordsForm(request.POST or None, request.FILES or None)
```

After form validation, the uploaded file is available as
`form.cleaned_data["file"]`.

### File-level validation

`read_import_rows()` checks the file before processing rows:

1. Extension must be `.csv` or `.json`.
2. File must be under 1 MB.
3. Contents must decode as UTF-8.
4. CSV must contain a `word` column.
5. JSON must be a list of objects.
6. The file must contain no more than 5,000 rows.

Invalid structure raises `ValueError`. The view attaches that message to the
form and renders the upload page again.

### Row-level processing

The view builds a case-insensitive set of the current user's existing words:

```python
existing_words = {
    value.casefold()
    for value in Word.objects.filter(owner=request.user)
    .values_list("word", flat=True)
}
```

It also tracks words imported earlier in the same file. Each row follows:

```text
read word text
  -> blank? count invalid
  -> existing or repeated? count duplicate
  -> build WordForm with row values
  -> validate
  -> assign current user as owner
  -> find/create current user's category
  -> save Word row
```

The imported row uses the same `WordForm`, so it receives the same word and
category rules as a normal web form. The file cannot choose another owner.

### Partial success

The page reports:

```text
imported   -> rows successfully saved
duplicates -> rows skipped because the word exists
invalid    -> blank or invalid rows
errors     -> first five readable row messages
```

A valid row can be imported even if a later row fails. The current loop saves
rows individually and does not use one `transaction.atomic()` around the
batch, so import behavior is partial-success rather than all-or-nothing.

## Complete sequences

```text
EDIT
GET /words/17/edit/
  -> owner-scoped lookup -> WordForm(instance=word)
  -> word_form.html -> POST edited fields + CSRF
  -> validate -> resolve category -> UPDATE dictionary_word
  -> message + 302 -> GET /words/17/

DELETE
GET /words/17/delete/
  -> owner-scoped lookup -> confirmation HTML only
  -> POST confirmation + CSRF -> owner-scoped lookup again
  -> DELETE dictionary_word -> message + 302 -> GET /words/

IMPORT
GET /words/import/ -> upload form
  -> POST multipart/form-data
  -> file checks -> parse rows -> owner-scoped duplicate set
  -> validate each row -> create categories and words
  -> render imported/duplicate/invalid summary
```

## Debugging checklist

```text
edit page 404             -> wrong ID or wrong owner
edit creates a new row   -> instance=word was omitted
delete happens on GET    -> confirmation boundary is wrong
bulk action leaks data   -> owner filter is missing
upload rejected          -> extension, size, encoding, or shape check
rows get wrong owner     -> server-side owner assignment is missing
duplicates slip through  -> casefold set or imported set is wrong
partial import surprises -> the batch is not atomic
```

Ask which boundary failed: browser to request, request to view, view to form,
form to ORM, ORM to database, or database to template.

## Files involved

- `pages/views.py`: edit, delete, bulk, import, and export orchestration.
- `pages/forms.py`: shared `WordForm` validation and category handling.
- `pages/import_export.py`: CSV/JSON parsing, limits, and response helpers.
- `pages/urls.py`: routes for each operation.
- `word_form.html`: create and edit form.
- `word_confirm_delete.html`: safe delete confirmation.
- `word_import.html`: multipart upload and summary.
- `word_detail.html`: edit and delete entry points.
- `dictionary/models.py`: `Word` and `Category` relationships.
