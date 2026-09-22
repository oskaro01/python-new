# Django Basics 13: Paginate Words

When a dictionary grows, showing every word on one page gets unwieldy.
This lesson shows five matching words at a time.

## Follow A Page Request

1. The view reads `q` and `category` from `request.GET` and filters the Word
   QuerySet, just like lesson 12.
2. `Paginator(words, 5)` divides the matching rows into pages of five.
3. `get_page(request.GET.get("page"))` selects a page from the URL. A missing
   page number means page 1. Django also handles invalid page numbers.
4. The template loops over that page's words. `has_previous` and `has_next`
   decide whether to show navigation links.

For example, `/words/?page=2` asks for the second group of five. A filtered
URL can be `/words/?q=calm&page=2`. The links carry `q` and `category` so the
filters stay active when moving between pages. `urlencode` makes entered
text safe to put in a URL.

## Try It

Start Django from the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

With six or more saved words, open `http://127.0.0.1:8000/words/` and click
**Next**. The sixth word should appear on page 2. Search or filter, then use
Previous/Next and check that your search stays in the URL. Stop the server
with `Ctrl+C`.

This lesson changes no model fields, so no migration is needed.

## Files Changed

- `pages/views.py`: paginate the filtered QuerySet.
- `pages/templates/pages/word_list.html`: page links and page number.
- `pages/static/pages/styles.css`: spacing for navigation.

## Key Memory Hook

```text
filter QuerySet -> Paginator -> one page -> template
```

## Next Lesson

Next: use Django messages to show feedback after saving, editing, or deleting.
