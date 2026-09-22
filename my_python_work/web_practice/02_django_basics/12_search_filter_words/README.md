# Django Basics 12: Search And Filter Words

The Words page now has a text search and an optional category filter. These
are GET inputs because they read saved data without changing it.

## Follow One Search

1. Open `/words/` and type `calm` into Search.
2. The form sends a GET request to `/words/?q=calm`.
3. `request.GET.get("q", "")` reads the value from the URL. `.strip()` removes
   spaces around it.
4. The view starts with `Word.objects.all()` and filters that QuerySet.
5. `Q(word__icontains=query) | Q(meaning__icontains=query) |
   Q(example__icontains=query)` means: show a word if any of those three
   fields contains the text. `icontains` ignores letter case.
6. The template shows matching words and keeps the search text in the input.

`Q` combines conditions with `|` (OR). The category filter uses
`category__iexact`, so it matches the whole category without caring about
letter case. If both inputs are filled, Django applies both filters (AND).
The database performs the filtering; the view does not scan every row in
Python.

Search here means **substring matching**, not typo correction. For example,
`cal` can match `calm`, but `clma` will not. We can revisit fuzzy search later.

## Try It

Start Django from the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Open `http://127.0.0.1:8000/words/`. Try part of a word, a meaning, and an
example. Then try a category and both inputs together. **Clear** returns to
the full list. Stop the server with `Ctrl+C`.

This lesson changes no model fields, so no migration is needed.

## Files Changed

- `pages/views.py`: read GET values and filter the Word QuerySet.
- `pages/templates/pages/word_list.html`: search form and empty results state.
- `pages/static/pages/styles.css`: responsive form spacing.

## Key Memory Hook

```text
GET values -> QuerySet filters -> matching database rows -> template
```

## Next Lesson

Next: paginate the list when it grows too long.
