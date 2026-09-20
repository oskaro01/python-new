# Lesson 02: GET Query Product Search

This lesson shows how search/filter pages work with query parameters.

Query parameters are the part after `?` in a URL:

```text
/products?search=python&category=books
```

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/02_get_query_products/app.py
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

- `GET` is good for search/filter pages.
- Search values can live in the URL.
- URLs can be bookmarked, refreshed, and shared.
- Python can read query parameters.
- Product list pages often use search, category, sorting, and pagination.

## Try These URLs

```text
http://127.0.0.1:8000/products
http://127.0.0.1:8000/products?search=python
http://127.0.0.1:8000/products?category=books
http://127.0.0.1:8000/product?id=2
```

## Key Memory Hook

```text
GET = read/search/filter
POST = submit/change/save
```

