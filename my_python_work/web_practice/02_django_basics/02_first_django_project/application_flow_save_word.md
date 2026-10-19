# Django Dictionary: End-to-End Save Flow

This document traces one real action in the current Django project: a signed-in
user saves a new word. The same architecture appears later in Checkout and
Chat: request, route, validation, business logic, persistence, and response.

## The map

```text
Browser
  -> HTTP request
manage.py / settings.py / urls.py
  -> pages view
  -> form validation and permission checks
  -> Django ORM and database
  -> redirect or rendered response
  -> browser updates
```

The browser never talks directly to SQLite or PostgreSQL. It talks to Django;
Django decides what the user may do and talks to the database for it.

## 1. Starting the application

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

`manage.py` sets `DJANGO_SETTINGS_MODULE` to `mini_site.settings` and passes
the command to Django. Django loads `settings.py`, which configures:

- installed apps: `pages`, `dictionary`, and `accounts`
- middleware for security, sessions, CSRF, authentication, and messages
- templates and static files
- SQLite locally, or PostgreSQL when `DATABASE_URL` exists

`mini_site/urls.py` is the top-level route table. It delegates the root paths
to `pages/urls.py` and the account paths to `accounts/urls.py`.

## 2. Opening the form

The browser requests:

```text
GET /words/new/
```

The request passes through middleware. `SessionMiddleware` reads the session
cookie, and `AuthenticationMiddleware` attaches the logged-in user to
`request.user`.

`pages/urls.py` matches `words/new/` and selects `views.new_word`.
`@login_required` runs before the view body. An anonymous visitor is sent to
login; an authenticated visitor continues.

For a GET request, the view creates an empty form:

```python
form = WordForm(user=request.user)
```

Then `render()` loads `pages/templates/pages/word_form.html`, replaces the
template variables, and returns HTML to the browser.

## 3. Submitting the form

The template contains a POST form and `{% csrf_token %}`. After the user types
the values and presses Save, the browser sends:

```text
POST /words/new/
Cookie: sessionid=...
Body: word=serene&meaning=calm...&csrfmiddlewaretoken=...
```

The browser sends strings, not a Python object or database row. Django must
validate those strings. CSRF middleware first checks that the submitted token
belongs to the browser's session.

The view creates a bound form:

```python
form = WordForm(request.POST, user=request.user)
```

`WordForm` is a `ModelForm`. Its model fields are `word`, `meaning`, `example`,
and `focus_first`. `category_name` is an extra form field used to find or
create a separate `Category` row.

## 4. Validation

The view calls:

```python
if form.is_valid():
```

This runs Django's normal field validation and the custom `clean_word()`
method. `clean_word()` strips whitespace and rejects words shorter than two
characters.

On failure:

```text
POST -> validation errors -> same template -> browser shows errors
```

No database row is created. On success, `form.cleaned_data` contains the
normalized values trusted by the application logic.

## 5. Ownership and category logic

Before saving, the view assigns:

```python
form.instance.owner = request.user
```

The browser does not choose the owner. The authenticated session does.

`WordForm.save()` uses `commit=False` so it can process the category first. It
looks for a category belonging to the same owner, case-insensitively:

```text
category exists -> reuse it
category missing -> create it for this owner
```

Then it attaches the category and calls `word.save()`.

## 6. Database write

The ORM translates `word.save()` into SQL. Locally it writes to `db.sqlite3`.
With a production `DATABASE_URL`, the same model operation writes to
PostgreSQL.

The resulting relationships look like this:

```text
auth_user
  id = 4, username = ayzal

dictionary_category
  id = 2, owner_id = 4, name = "calm"

dictionary_word
  id = 17, owner_id = 4, word = "serene"
  meaning = "calm and peaceful", category_id = 2
```

Migrations create the table structure. The form save creates the actual data
row. A migration is the blueprint/change history; a saved model is application
data.

The model also supplies timestamps, foreign keys, indexes, and the custom
`view_all_words` permission.

## 7. Redirect and list page

After saving, the view clears the staff statistics cache, adds a one-time
success message, and returns:

```python
return redirect("pages:word_list")
```

Django sends HTTP 302. The browser follows it with:

```text
GET /words/
```

This is POST/Redirect/GET. Refreshing the list page therefore does not submit
the original form again.

The list view queries:

```python
Word.objects.select_related("category").filter(owner=request.user)
```

`filter(owner=request.user)` is the privacy boundary. `select_related()` loads
the related category efficiently. Search adds conditions for the word,
meaning, and example. Ordering places focus-first words at the top, and
`Paginator` limits the page to 50 rows.

The QuerySet is evaluated when the template needs the results. Django renders
`word_list.html`, escapes user-provided text, and sends the final HTML to the
browser.

## Complete sequence

```text
click Save
  -> POST /words/new/
  -> session/authentication middleware
  -> CSRF check
  -> URL resolver -> pages.views.new_word
  -> WordForm(request.POST, user=request.user)
  -> is_valid() -> clean_word() -> cleaned_data
  -> assign owner from request.user
  -> find/create owner-scoped Category
  -> INSERT dictionary_word
  -> success message + HTTP 302
  -> GET /words/
  -> owner-filtered QuerySet + pagination
  -> word_list.html
  -> HTML response in browser
```

## What can go wrong

Trace the same boundaries while debugging:

1. Page does not open: URL pattern or server startup.
2. Redirects to login: authentication or session cookie.
3. CSRF failure: missing or mismatched form token.
4. Form errors: `WordForm` or `clean_word()`.
5. Form succeeds but row is missing: `save()`, migrations, or database.
6. Row exists but is invisible: owner filter or wrong user session.
7. Template crashes: missing context variable or template syntax.
8. Local works but production fails: environment variables, database URL,
   migrations, static files, or deployment logs.

Ask which boundary failed: browser to request, request to view, view to form,
form to ORM, ORM to database, or database to template.

## Files involved

- `manage.py`: Django command entry point.
- `mini_site/settings.py`: project configuration.
- `mini_site/urls.py`: top-level routing.
- `pages/urls.py`: word routes.
- `pages/views.py`: request orchestration.
- `pages/forms.py`: validation and category handling.
- `dictionary/models.py`: database tables and relationships.
- `pages/templates/pages/word_form.html`: submitted form.
- `pages/templates/pages/word_list.html`: rendered list.
- `db.sqlite3`: local database; production uses PostgreSQL when configured.
