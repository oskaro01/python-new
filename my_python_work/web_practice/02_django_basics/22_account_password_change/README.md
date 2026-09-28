# Django Basics 22: Account Page And Password Change

This lesson adds a small account page and Django's built-in password-change
workflow.

## What We Added

- An account page at `/accounts/account/`.
- Username, email, word count, and category count.
- A password-change form at `/accounts/password-change/`.
- A success page after changing the password.
- An Account link for logged-in users.

## Password Reset Vs Password Change

These features solve different problems:

```text
Password reset
    You forgot the password.
    Django emails a temporary link.
    You do not need to be logged in.

Password change
    You know the current password.
    You must already be logged in.
    Django asks for the current password before saving the new one.
```

Password change does not need a migration. It uses Django's existing User
model and `PasswordChangeForm`.

## Try It

1. Log in.
2. Open `/accounts/account/`.
3. Click **Change password**.
4. Enter the current password and a new password.
5. Log out.
6. Log in again with the new password.

If you visit the password-change URL while logged out, Django sends you to the
login page instead.

## Main Flow

```text
logged-in user
    -> account page
    -> password change form
    -> current password check
    -> new password saved
    -> success page
```

The built-in form handles password validation and secure password hashing.
We do not store the password ourselves.

## Files

- `accounts/views.py`: loads account information.
- `accounts/urls.py`: connects account and password-change routes.
- `accounts/templates/accounts/account.html`: shows the account page.
- `accounts/templates/accounts/password_change_form.html`: renders the form.
- `accounts/templates/accounts/password_change_done.html`: confirms success.
- `pages/templates/pages/base.html`: adds the Account navigation link.

## Key Memory Hook

```text
reset = forgot password
change = logged in and know current password
```

## Next Lesson

Next: import and export dictionary words with CSV and JSON.
