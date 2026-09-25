# Django Basics 17: Register, Login, And Logout

This lesson begins Phase 5 of our roadmap: user accounts. Visitors can now
register, log in, and log out using Django's built-in authentication system.

## What Django Provides

Django already includes a User model, password hashing, sessions, login and
logout logic, and secure authentication forms. We use those tools instead of
building password handling ourselves.

Our new `accounts` app owns the account pages:

- `RegisterForm` extends Django's `UserCreationForm`.
- `register()` saves a valid user and logs them in immediately.
- `LoginView` validates the username and password.
- `LogoutView` ends the current login session.
- `base.html` checks `user.is_authenticated` to choose which links to show.

## Follow Registration

1. The visitor opens `/accounts/register/` with GET.
2. The view displays an empty `RegisterForm`.
3. POST sends the username and two password fields with a CSRF token.
4. `form.is_valid()` checks the username, matching passwords, and password
   rules.
5. `form.save()` creates the User with a hashed password.
6. `login(request, user)` stores the user's ID in their session.
7. The view redirects to the Words page and shows a success message.

The database never stores the plain password. It stores a one-way hash used
to check future login attempts.

## Follow Login And Logout

`LoginView` receives the login form and starts a session when the credentials
are correct. `LOGIN_REDIRECT_URL` sends a successful login to the Words page.

Logout uses a small POST form in the navigation with a CSRF token. After
`LogoutView` clears the session, `LOGOUT_REDIRECT_URL` returns to Words.

## Try It

Run Django from the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Open `http://127.0.0.1:8000/accounts/register/`, create a test account, and
notice your username in the navigation. Log out, then log back in at
`http://127.0.0.1:8000/accounts/login/`. Stop the server with `Ctrl+C`.

The built-in auth tables came from the migrations you already applied. This
lesson adds no custom model, so it needs no new migration.

## Files Added Or Changed

- `accounts/`: registration form, account views, URLs, and templates.
- `mini_site/settings.py`: register the app and set redirect destinations.
- `mini_site/urls.py`: include `/accounts/` routes.
- `pages/templates/pages/base.html`: authenticated navigation.
- `pages/static/pages/styles.css`: account form and navigation styles.

## Key Memory Hook

```text
register -> create User -> login session
login -> verify password -> login session
logout POST -> clear login session
```

## Next Lesson

Lesson 18 connects every Word to its owner and keeps each user's dictionary
private.
