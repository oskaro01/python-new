# Django Basics 20: Password Reset

This lesson adds a complete password reset workflow using Django's built-in
authentication views.

## What We Added

- An email field during registration.
- A "Forgot your password?" link on the login page.
- A password reset form.
- A reset link printed in the terminal.
- A form for choosing a new password.
- Success and expired-link pages.

## Why The Email Prints In The Terminal

We are learning locally, so `settings.py` uses:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

Django behaves as if it sent an email, but prints the email contents in the
terminal instead. Later we can replace this with SMTP or Resend.

## Try The Full Flow

1. Register a new account with an email address.
2. Open `/accounts/password-reset/`.
3. Submit that email address.
4. Look at the terminal running Django.
5. Copy the reset link from the printed email.
6. Open the link in the browser.
7. Choose a new password.
8. Log in with the new password.

There is no migration for this lesson. Django's built-in User table already
has an email field.

## Main Idea

The built-in views handle the security-sensitive parts:

```text
PasswordResetView
    -> creates a temporary token
    -> sends a reset link
PasswordResetConfirmView
    -> checks the token
    -> saves the new password
```

The token is temporary and tied to the user, so we do not create reset tokens
ourselves.

## Files

- `accounts/forms.py`: asks new users for an email address.
- `accounts/urls.py`: connects Django's reset views.
- `mini_site/settings.py`: uses the local console email backend.
- `accounts/templates/accounts/password_reset_*.html`: reset pages.
- `accounts/templates/accounts/password_reset_email.txt`: email body.
- `accounts/templates/accounts/password_reset_subject.txt`: email subject.

## Key Memory Hook

```text
email -> temporary reset link -> new password
```

## Next Lesson

Next: ManyToMany relationships with reusable tags. We are postponing that
feature until it becomes useful.
