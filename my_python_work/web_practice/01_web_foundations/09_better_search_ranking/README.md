# Lesson 09: Better Search And Ranking

Lesson 08 used strict SQL search:

```text
name LIKE "%python%"
```

That is useful, but it does not understand typos like:

```text
pyton
djngo
notebok
```

This lesson adds a beginner-friendly ranking layer.

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/09_better_search_ranking/app.py
```

Open the URL printed in the terminal.

Usually it is:

```text
http://127.0.0.1:8000/products
```

If port `8000` is busy, the app will try `8001`, `8002`, or `8003`.

## What This Teaches

- Strict search finds exact text inside a field.
- Fuzzy search finds close spellings.
- Ranking decides which result should appear first.
- Category filtering can happen in SQL.
- Search ranking can happen in Python.
- Better search usually combines multiple techniques.

## Try These Searches

```text
python
pyton
django
djngo
notebok
security
```

## Key Memory Hook

```text
Filter = remove things that cannot match
Rank = sort possible matches from best to weakest
Fuzzy = close enough spelling
```

## Django Preview

Later we can do simple search with Django QuerySets, then eventually use PostgreSQL full-text search.
