# Django Basics 31: Gmail SMTP Email

Lesson 20 used Django's console email backend. Reset links appeared in the
terminal, which was perfect for local learning.

Now we are connecting the live app to Gmail SMTP so password-reset messages
can really be delivered.

## Cost

```text
cost: $0
custom domain: not required
credit card: not required for this setup
```

Use a separate Gmail account for the app if possible. It keeps the learning
project separate from your personal mailbox.

## Important Security Rule

Never put these values in Python files or Git:

```text
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
```

The password is a Google App Password, not your normal Gmail password.

## Part A: Google Setup

You already completed these steps:

1. Turn on Google 2-Step Verification.
2. Open Google App Passwords.
3. Create an app password named `personal-dictionary`.
4. Copy the generated 16-character value privately.

Google may display spaces in the app password. When entering it into Render,
use the generated characters without the display spaces.

Do not send the app password in chat or commit it.

## Part B: Django Settings

File:

```text
mini_site/settings.py
```

Django reads these settings from environment variables:

```text
DJANGO_EMAIL_BACKEND
EMAIL_HOST
EMAIL_PORT
EMAIL_USE_TLS
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL
```

The safe local default remains:

```python
django.core.mail.backends.console.EmailBackend
```

So local password-reset links still print in the terminal unless you
explicitly select SMTP.

The Gmail SMTP values are:

```text
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-app-email@gmail.com
EMAIL_HOST_PASSWORD=your-google-app-password
DEFAULT_FROM_EMAIL=your-app-email@gmail.com
```

Port `587` uses TLS. TLS encrypts the connection while Django talks to
Gmail's SMTP server.

## Part C: Add The Values To Render

Open:

```text
Render -> personal-dictionary -> Environment
```

Add or update these variables:

| Name | Value |
| --- | --- |
| `DJANGO_EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | your Gmail address |
| `EMAIL_HOST_PASSWORD` | your Google App Password |
| `DEFAULT_FROM_EMAIL` | the same Gmail address |

Render's `render.yaml` also describes these values. The two secret fields
remain `sync: false` so the password is entered privately in Render.

Save the variables and trigger a redeploy if Render does not redeploy
automatically.

## Part D: Test Password Reset Online

1. Open the live dictionary.
2. Log out.
3. Open the password reset page.
4. Enter the email address of an existing account.
5. Submit the form.
6. Check that mailbox's inbox and spam folder.
7. Open the reset link.
8. Choose a new password.
9. Log in with the new password.

The live Render logs should not print the full email password or connection
string.

## Part E: Optional Local Test

To test Gmail from your computer without permanently saving the credentials,
open PowerShell at the repository root and set variables only for that
terminal window:

```powershell
$env:DJANGO_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "True"
$env:EMAIL_HOST_USER = Read-Host "Gmail address"
$env:EMAIL_HOST_PASSWORD = Read-Host "Google App Password"
$env:DEFAULT_FROM_EMAIL = $env:EMAIL_HOST_USER
```

Start Django:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py runserver
```

Use the password-reset form and check the recipient mailbox.

When finished, remove the temporary values:

```powershell
Remove-Item Env:DJANGO_EMAIL_BACKEND -ErrorAction SilentlyContinue
Remove-Item Env:EMAIL_HOST -ErrorAction SilentlyContinue
Remove-Item Env:EMAIL_PORT -ErrorAction SilentlyContinue
Remove-Item Env:EMAIL_USE_TLS -ErrorAction SilentlyContinue
Remove-Item Env:EMAIL_HOST_USER -ErrorAction SilentlyContinue
Remove-Item Env:EMAIL_HOST_PASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:DEFAULT_FROM_EMAIL -ErrorAction SilentlyContinue
```

Closing PowerShell also removes variables created in that session.

## Part F: Keep Local Development Simple

If you do not set the SMTP variables, local Django continues using:

```text
console email backend -> reset link printed in terminal
```

That is often more convenient while coding.

The live Render service uses:

```text
Gmail SMTP -> real email delivery
```

## Common Problems

### Authentication failed

Check that:

- 2-Step Verification is enabled.
- You used a Google App Password.
- You did not use your normal Gmail password.
- The app password has no accidental extra spaces.
- `EMAIL_HOST_USER` is the Gmail account that created the app password.

### Email does not arrive

Check:

- spam/junk folder
- recipient email spelling
- Render deployment logs
- `DEFAULT_FROM_EMAIL`
- whether the Render variables were saved

The app logs safe password-reset checkpoints:

```text
Password reset requested for email domain gmail.com: 1 eligible user(s).
Password reset SMTP send returned 1 message(s) for gmail.com.
```

How to read them:

| Log result | Meaning |
| --- | --- |
| `0 eligible user(s)` | No active user with that exact email and a usable password exists in the live database. |
| `1 eligible user(s)` then `Password reset SMTP send failed` | Gmail rejected the send or the connection failed. The log includes the exception type. |
| `1 eligible user(s)` and `send returned 1 message(s)` | Django handed the email to Gmail. Check Gmail Sent, search, spam, all mail, and sender reputation. |
| `send returned 0 message(s)` | The backend did not report a delivered message. Check the SMTP configuration and deployment variables. |

### `SMTPAuthenticationError`

The Gmail account rejected the login. Generate a new App Password and replace
the Render `EMAIL_HOST_PASSWORD` value. Do not put it in Git.

### Local reset still prints in the terminal

That is expected when `DJANGO_EMAIL_BACKEND` is not set locally. The live
Render service has its own environment variables.

## What We Learned

```text
console backend -> useful during local development
SMTP backend    -> sends through a mail provider
environment vars -> keep credentials outside the repository
app password    -> safer than using the normal account password
```

## Official References

- Django email settings: https://docs.djangoproject.com/en/6.1/topics/email/
- Google App Passwords: https://support.google.com/accounts/answer/185833
- Gmail SMTP settings: https://support.google.com/a/answer/176600

## Next Lesson

Next: a small health-check endpoint and deployment observability.
