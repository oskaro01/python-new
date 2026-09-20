# Lesson 08: Database Search, Filter, And Pagination

This lesson combines earlier ideas:

```text
GET query parameters + SQLite database + product list page
```

This is much closer to a real ecommerce category/search page.

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/08_database_search_pagination/app.py
```

Open:

```text
http://127.0.0.1:8000/products
```

Stop:

```text
Ctrl+C
```

## What This Teaches

- Searching database rows with `LIKE`
- Filtering rows by category
- Counting total matching rows
- Showing only a few rows per page
- Using `LIMIT` and `OFFSET`
- Keeping search/filter values in the URL
- Building previous/next page links

## Try These URLs

```text
http://127.0.0.1:8000/products
http://127.0.0.1:8000/products?search=python
http://127.0.0.1:8000/products?category=Books
http://127.0.0.1:8000/products?search=django&category=Courses
http://127.0.0.1:8000/products?page=2
```

## Key Memory Hook

```text
Search = WHERE name LIKE ?
Filter = WHERE category = ?
Pagination = LIMIT + OFFSET
```

## Django Preview

Later Django will make this easier with QuerySets:

```python
Product.objects.filter(name__icontains="python")
```

