# Lesson 05: Templates And Static Files

So far, our Python files built HTML using giant strings.

That works for learning, but real web apps separate things:

```text
Python = logic
HTML templates = page structure
CSS static files = styling
```

Django will later do this properly with its template system and static file tools.

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/05_templates_static_files/app.py
```

Open:

```text
http://127.0.0.1:8000
```

Stop:

```text
Ctrl+C
```

## What This Teaches

- HTML can live in separate template files.
- CSS can live in a separate static file.
- Python can load a template from disk.
- Python can fill placeholders like `{{ title }}`.
- A browser requests CSS separately from the HTML page.
- Routes can return pages while `/static/...` returns files.

## Files

- `app.py`
- `templates/base.html`
- `templates/home.html`
- `templates/products.html`
- `static/styles.css`

## Try This

1. Open `/`.
2. Open `/products`.
3. Change a color in `static/styles.css`.
4. Refresh the browser.
5. Change some text in `templates/home.html`.
6. Refresh again.

Notice how you can edit the page without touching the Python logic.

## Key Memory Hook

```text
Template = HTML with placeholders
Static file = CSS/image/JS file served as-is
```

