# Django Dictionary: Authentication and Session Flow

This document follows registration, login, a protected page, and logout in
the current Dictionary project. Authentication is the bridge between “a
browser visitor” and “this user's private Word rows.”

## The central idea

```text
password form
  -> Django authentication form
  -> database user lookup + password hash check
  -> session row containing the user identity
  -> sessionid cookie in the browser
  -> request.user on later requests
  -> login_required and owner filters protect data
```

The browser does not receive the user's password back. It receives a session
cookie. The cookie points Django to server-side session data.

## 1. A visitor requests a protected page

Suppose an anonymous visitor opens:

```text
GET /words/
```

`pages/urls.py` selects `views.word_list`. That view has `@login_required`.
The decorator sees that `request.user.is_authenticated` is false, so it does
not run the word query. It redirects to a login URL similar to:

```text
/accounts/login/?next=/words/
```

`next` remembers the page the visitor originally wanted.

This is the first privacy boundary: an unauthenticated request cannot reach
the private dictionary query.

## 2. Login page GET

`mini_site/urls.py` includes `accounts.urls`. That file maps:

```python
path(
    "login/",
    auth_views.LoginView.as_view(template_name="accounts/login.html"),
    name="login",
)
```

The built-in `LoginView` handles the GET request. It creates Django's
`AuthenticationForm` and renders `accounts/login.html`. That template includes
the CSRF token and preserves `next` in a hidden field.

The page contains username and password inputs. The password input is sent to
the server only during the POST; it is never placed into a URL query string.

## 3. Login POST

The browser submits:

```text
POST /accounts/login/
username=ayzal
password=...
csrfmiddlewaretoken=...
next=/words/
```

Middleware runs first:

1. Session middleware reads the existing anonymous session, if one exists.
2. CSRF middleware checks the form token.
3. Authentication middleware exposes the current anonymous user object.

Then `LoginView` gives the submitted values to `AuthenticationForm`.

## 4. Password verification

The authentication form asks Django's authentication backend to authenticate
the submitted username and password. Django finds the row in `auth_user` and
compares the submitted password with the stored password hash.

The database does not contain:

```text
password = "2458"
```

It contains a salted, one-way password hash. Django's `UserCreationForm` uses
`set_password()` when a user is created, and the authentication backend uses
Django's password checker during login.

There are two outcomes:

```text
valid credentials   -> authenticated user object
invalid credentials -> form error, no login, no session identity change
```

The application does not manually compare plaintext passwords.

## 5. What registration does

Registration uses `accounts/views.py` instead of the generic login view.

```python
form = RegisterForm(request.POST)
if form.is_valid():
    user = form.save()
    login(request, user)
```

`RegisterForm` subclasses Django's `UserCreationForm` and adds a required
email field. The form validates username rules, password rules, and matching
password fields. `form.save()` creates an `auth_user` row and hashes the
password before the row is written.

The custom view immediately calls `login(request, user)`, so a new account is
authenticated without requiring a second manual login. It then adds a success
message and redirects to the word list.

The important registration sequence is:

```text
POST /accounts/register/
  -> RegisterForm validation
  -> UserCreationForm password hashing
  -> INSERT auth_user
  -> create/rotate session identity
  -> success message
  -> redirect /words/
```

## 6. How `login()` changes the session

After successful authentication, Django's `login(request, user)` does not put
the password into the cookie. It associates the user with the session and
rotates the session key to reduce session-fixation risk.

Conceptually, server-side session data becomes:

```text
session_key: generated opaque value
_auth_user_id: 4
_auth_user_backend: django.contrib.auth.backends.ModelBackend
_auth_user_hash: user-session hash
```

The browser receives a `sessionid` cookie containing only the opaque session
key. On a later request, Django uses that key to recover the user ID.

## 7. The first authenticated request

The browser follows the redirect:

```text
GET /words/
Cookie: sessionid=<opaque value>
```

`SessionMiddleware` loads the session. `AuthenticationMiddleware` reads the
stored user ID and attaches a lazy user object as `request.user`.

The same `word_list` view now passes `@login_required`. Its query is:

```python
Word.objects.select_related("category").filter(owner=request.user)
```

Authentication answers “who is this?” The owner filter answers “which rows may
this user see?” Both are needed. A logged-in user must still be blocked from
another user's words.

## 8. The navigation bar uses the same identity

The shared `pages/base.html` template receives the authenticated user through
Django's auth context processor. It can therefore use:

```django
{% if user.is_authenticated %}
    {{ user.username }}
    <form method="post" action="{% url 'accounts:logout' %}">
        {% csrf_token %}
        <button type="submit">Log out</button>
    </form>
{% else %}
    <a href="{% url 'accounts:login' %}">Log in</a>
{% endif %}
```

The template does not perform authentication. It only displays the result
that middleware already attached to the request.

## 9. Logout

Logout is a POST form in the navigation bar:

```text
POST /accounts/logout/
```

The built-in `LogoutView` clears the authenticated session data. The browser's
next request no longer resolves to the previous user. The configured
`LOGOUT_REDIRECT_URL` sends the visitor to the word list, where protected views
will redirect to login again.

Using POST and CSRF protection makes logout an intentional state-changing
action rather than a casual GET link.

## 10. Account page

`/accounts/account/` is protected by `@login_required`. Once allowed, the view
uses the authenticated relationships:

```python
request.user.words.count()
request.user.word_categories.count()
```

These reverse relationships come from the model `related_name` values:

```python
Word.owner -> related_name="words"
Category.owner -> related_name="word_categories"
```

The account page is therefore a live database summary for the current user,
not a value stored in the browser.

## 11. Password changes and reset

Password change is protected with `login_required` and uses Django's built-in
`PasswordChangeView`. The user must prove the current password, enter a new
password, and pass the password validators. Django updates the stored hash.

Password reset is different because the user may be anonymous. The reset form
accepts an email, generates a time-limited token, and sends a link through the
configured email backend. The link contains a user identifier and token, not
the password. The user submits a new password, Django validates it, stores a
new hash, and invalidates the token's usefulness.

Locally, the console email backend prints the message in the terminal. A
production environment can use Gmail SMTP or Resend through environment
variables.

## Complete login sequence

```text
GET /words/
  -> login_required sees AnonymousUser
  -> HTTP 302 to /accounts/login/?next=/words/
  -> LoginView renders AuthenticationForm
  -> user submits username, password, and CSRF token
  -> CSRF middleware validates token
  -> AuthenticationForm checks auth_user password hash
  -> login(request, user)
  -> session stores authenticated user ID
  -> browser receives sessionid cookie
  -> HTTP 302 to next=/words/
  -> SessionMiddleware loads sessionid
  -> AuthenticationMiddleware sets request.user
  -> owner-filtered Word query runs
  -> word_list.html renders private words
```

## Security boundaries

- Passwords are hashed by Django; they are not stored as plaintext.
- CSRF tokens protect registration, login, logout, and other POST forms.
- Sessions carry an opaque key; the browser does not choose a user ID.
- `login_required` stops unauthenticated access.
- Word queries filter by `owner=request.user`.
- Templates escape user-provided values before placing them in HTML.
- Logout clears authentication state instead of merely hiding navigation.
- Password reset uses time-limited tokens instead of emailing passwords.

## Debugging checklist

```text
login page missing       -> accounts/urls.py and template path
always returns to login  -> session cookie, login settings, or auth middleware
invalid credentials      -> username, password hash, or authentication backend
CSRF error               -> token and session/cookie behavior
wrong user's words       -> owner assignment or owner-filtered QuerySet
logout appears ineffective -> POST action and session cookie
reset email missing      -> EMAIL_BACKEND, SMTP/Resend settings, and logs
```

The boundary question is: “Did Django identify the user, store the session,
load the session on the next request, and apply that identity to the query?”

## Files involved

- `accounts/forms.py`: registration and password-reset form behavior.
- `accounts/views.py`: registration and account page flow.
- `accounts/urls.py`: login, logout, registration, and password routes.
- `accounts/templates/accounts/login.html`: login POST form.
- `accounts/templates/accounts/register.html`: registration POST form.
- `mini_site/settings.py`: auth middleware, session settings, and redirects.
- `pages/views.py`: protected dictionary views and owner filters.
- `pages/templates/pages/base.html`: authenticated navigation and logout form.
- `dictionary/models.py`: user relationships for words and categories.
