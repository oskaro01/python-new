# Django Basics 23: CSV And JSON Import/Export

This lesson lets each logged-in user back up and restore their own dictionary.

## What We Added

- Export your words as CSV.
- Export your words as JSON.
- Upload a CSV or JSON backup.
- Skip duplicate words.
- Validate imported rows with the existing `WordForm`.
- Keep imported words owned by the logged-in user.
- Show an import summary.

## Try It

1. Log in and open `/words/`.
2. Click **Export CSV** or **Export JSON**.
3. Open `/words/import/`.
4. Upload the downloaded file.
5. Review the imported, duplicate, and invalid row counts.

Export includes:

```text
word, meaning, example, category
```

## CSV Example

```csv
word,meaning,example,category
serene,calm and peaceful,The lake was serene.,adjective
stern,serious and unrelenting,The teacher looked stern.,adjective
```

## JSON Example

```json
[
  {
    "word": "serene",
    "meaning": "calm and peaceful",
    "example": "The lake was serene.",
    "category": "adjective"
  }
]
```

## Safety Rules

The import accepts only:

- UTF-8 `.csv` or `.json` files
- Files smaller than 1 MB
- Rows with a valid word

Duplicate words are compared without caring about letter case. For example,
`Serene` and `serene` count as duplicates for the same user.

The import never trusts an owner value from the file. Every new row receives:

```python
owner = request.user
```

That keeps one user from importing words into another user's dictionary.

## Why Use Both Formats?

```text
CSV  -> easy to open and edit in a spreadsheet
JSON -> keeps a structured backup for Python programs
```

The same data can later be imported into another tool or used for a review
workflow.

## Files

- `pages/import_export.py`: CSV/JSON reading and download helpers.
- `pages/forms.py`: upload validation.
- `pages/views.py`: owner-safe export and import views.
- `pages/templates/pages/word_import.html`: upload form and summary.
- `pages/templates/pages/word_list.html`: import and export links.

## Key Memory Hook

```text
export = database rows -> file
import = file rows -> validated database rows
```

## Next Lesson

Next: custom staff dashboard and analytics.
