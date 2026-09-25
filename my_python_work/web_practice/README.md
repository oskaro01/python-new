# Web Practice

This folder starts the Python full-stack path.

We learned web foundations first; now the Django lessons build on them:

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
12. `02_django_basics/02_first_django_project/`
13. `02_django_basics/03_first_django_app/`
14. `02_django_basics/04_django_templates/`
15. `02_django_basics/05_django_static_files/`
16. `02_django_basics/06_django_forms/`
17. `02_django_basics/07_django_models_migrations/`
18. `02_django_basics/08_save_words_to_database/`
19. `02_django_basics/09_word_detail_404/`
20. `02_django_basics/10_edit_saved_word/`
21. `02_django_basics/11_delete_saved_word/`
22. `02_django_basics/12_search_filter_words/`
23. `02_django_basics/13_paginate_words/`
24. `02_django_basics/14_django_messages/`
25. `02_django_basics/15_django_admin/`
26. `02_django_basics/16_django_modelform/`
27. `02_django_basics/17_auth_register_login_logout/`
28. `02_django_basics/18_private_words_ownership/`

## Django Run Helper

For activation, deactivation, running, and stopping Django:

```text
HOW_TO_RUN_DJANGO.md
```

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

## Run The First Django Project

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

The first app lesson also adds:

```text
http://127.0.0.1:8000/about/
http://127.0.0.1:8000/words/new/
http://127.0.0.1:8000/words/
```

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
- A Django project starts with `manage.py`, `settings.py`, and `urls.py`.
- A Django app is one feature area inside a project.
- Django templates let views return HTML files with context data.
- Django static files keep CSS, images, and JavaScript outside templates.
- Django forms validate submitted `POST` data before we trust it.
- Django models describe database tables using Python classes.
- A validated Django form can create a database row; a QuerySet can read it back.
- A detail route can fetch one row by ID or return a 404.
- An edit form can load current values and save changes to the same row.
- A confirmation page can delete a row only after a POST request.
- QuerySets can search saved words, meanings, and examples.
- Django's Paginator can show a few filtered words per page.
- Django messages show one-time feedback after a redirect.
- Django admin can manage registered Word rows with an admin account.
- ModelForm connects Word fields, validation, and saving.
- Django auth provides secure registration, login, logout, and sessions.
- A ForeignKey and owner-filtered queries keep each user's words private.
