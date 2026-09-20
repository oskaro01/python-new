# Lesson 06: Dynamic Routes And 404 Pages

This lesson shows how one route can handle many pages.

Example:

```text
/products/1
/products/2
/products/3
```

The route pattern is:

```text
/products/<product_id>
```

Django will later do this with URL patterns like `path("products/<int:id>/", view)`.

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/app.py
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

- A dynamic route can use part of the URL as data.
- `/products/1` means product detail for product ID `1`.
- Python can split the URL path into parts.
- A real app needs useful 404 pages.
- Product list pages link to product detail pages.
- Status codes matter: success is `200`, not found is `404`.

## Files

- `app.py`
- `templates/base.html`
- `templates/products.html`
- `templates/product_detail.html`
- `templates/not_found.html`
- `static/styles.css`

## Try These URLs

```text
http://127.0.0.1:8000/products
http://127.0.0.1:8000/products/1
http://127.0.0.1:8000/products/999
http://127.0.0.1:8000/anything-weird
```

## Key Memory Hook

```text
Static route = exact path
Dynamic route = path with a variable piece
404 = the server understood the request, but no matching page exists
```

