# Web Practice

This folder starts the Python full-stack path.

We are not jumping straight into Django yet. First we learn what Django will later do for us:

- receive a browser request
- choose what page to show
- send back HTML
- handle a form
- read GET and POST data

## Study Order

1. `01_web_foundations/01_request_response/`
2. `01_web_foundations/02_get_query_products/`
3. `01_web_foundations/03_post_json_guestbook/`
4. `01_web_foundations/04_cookies_sessions_cart/`
5. `01_web_foundations/05_templates_static_files/`
6. `01_web_foundations/06_dynamic_routes_404/`
7. `01_web_foundations/07_sqlite_database_basics/`
8. `01_web_foundations/08_database_search_pagination/`
9. `01_web_foundations/09_better_search_ranking/`
10. `01_web_foundations/10_file_uploads_media/`
11. `02_django_basics/01_setup_django_environment/`
12. Later: first Django project

## Run The First Server

```powershell
python -B my_python_work/web_practice/01_web_foundations/01_request_response/simple_server.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Run The Second Server

Stop the first server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/02_get_query_products/app.py
```

Then open:

```text
http://127.0.0.1:8000/products
```

## Run The Third Server

Stop the second server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/03_post_json_guestbook/app.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Run The Fourth Server

Stop the third server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/04_cookies_sessions_cart/app.py
```

Then open:

```text
http://127.0.0.1:8000/products
```

## Run The Fifth Server

Stop the fourth server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/05_templates_static_files/app.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Run The Sixth Server

Stop the fifth server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/app.py
```

Then open:

```text
http://127.0.0.1:8000/products
```

## Run The Seventh Server

Stop the sixth server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/07_sqlite_database_basics/app.py
```

Then open:

```text
http://127.0.0.1:8000/products
```

## Run The Eighth Server

Stop the seventh server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/08_database_search_pagination/app.py
```

Then open:

```text
http://127.0.0.1:8000/products
```

## Run The Ninth Server

Stop the eighth server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/09_better_search_ranking/app.py
```

Then open the URL printed in the terminal.

## Run The Tenth Server

Stop the ninth server with `Ctrl+C`, then run:

```powershell
python -B my_python_work/web_practice/01_web_foundations/10_file_uploads_media/app.py
```

Then open the URL printed in the terminal.

## Check Django Setup

After the web foundation lessons, check whether Django is installed:

```powershell
python -B my_python_work/web_practice/02_django_basics/01_setup_django_environment/check_setup.py
```

If Django is missing, follow that lesson's README.

## What To Notice

- A URL points to a route.
- The browser sends a request.
- Python sends back a response.
- The response can be HTML.
- A form can send data back to Python.
- `GET` usually reads data.
- `POST` usually changes/submits data.
- Query parameters are the part after `?` in a URL.
- Search/filter pages often use `GET`.
- Submitted data can be saved to JSON before we learn databases.
- Cookies and sessions let a website remember a visitor's cart.
- Templates and static files keep Python, HTML, and CSS separated.
- Dynamic routes use part of the URL as data, like `/products/1`.
- SQLite stores growing app data in database tables.
- Search, filter, and pagination make database lists easier to browse.
- Better search can rank results and handle close spellings.
- File upload forms send file bytes with `multipart/form-data`.
- Django needs a Python environment with Django installed before a project can run.
