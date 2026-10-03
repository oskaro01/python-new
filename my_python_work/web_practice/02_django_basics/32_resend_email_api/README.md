# Django Basics 32: Resend Email API

Render's free web service cannot open outbound SMTP connections. That is why
Gmail SMTP failed with:

```text
OSError: [Errno 101] Network is unreachable
```

This lesson sends email through Resend's HTTPS API instead. HTTPS works from
the Render free service, and the existing Django password-reset view can keep
using Django's email interface.

## Cost

```text
Resend free plan: suitable for learning
custom domain: not required for the first test
credit card: not required for the first test
```

Free-provider limits can change, so check Resend's current dashboard before
using this for a real production application.

## Part A: Keep The API Key Private

Create a Resend API key and store it only in Render's environment variables.
Never put it in Python files, screenshots, chat, or Git.

```text
RESEND_API_KEY=private-value
```

## Part B: Choose The Sender

Set `RESEND_FROM_EMAIL` to a sender Resend allows for your account.

For an initial test, this is commonly:

```text
onboarding@resend.dev
```

If Resend rejects that sender, verify a sender or domain in Resend and use the
approved address instead.

The recipient should be the email address of an existing dictionary user.

## Part C: Configure Render

Open:

```text
Render -> personal-dictionary -> Environment
```

Set these values:

| Name | Value |
| --- | --- |
| `DJANGO_EMAIL_BACKEND` | `accounts.email_backend.ResendEmailBackend` |
| `RESEND_API_KEY` | your private Resend API key |
| `RESEND_FROM_EMAIL` | the approved Resend sender |
| `DEFAULT_FROM_EMAIL` | the same approved Resend sender |

The old Gmail variables are no longer used by the live app. You can remove
`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, and
`EMAIL_HOST_PASSWORD` from Render after switching the backend.

Save the variables and redeploy.

## Part D: Test Password Reset

1. Wait for Render to show the new deployment as live.
2. Open the password-reset page.
3. Submit the exact email address of an existing user.
4. Check the recipient inbox, spam, and all mail.
5. Search for:

```text
subject:"Password reset for your Personal Dictionary"
```

Useful Render log lines:

```text
Password reset requested for email domain gmail.com: 1 eligible user(s).
Resend accepted email email_123 for 1 recipient(s).
```

The first line confirms the live database found the user. The second means
Resend accepted the API request.

If the API rejects the sender or key, the logs will show a safe error without
printing the API key.

## Part E: Local Development

Leave `DJANGO_EMAIL_BACKEND` unset locally while learning. Django then uses the
console backend and prints reset links in the terminal.

To test the Resend backend locally, set temporary PowerShell variables:

```powershell
$env:DJANGO_EMAIL_BACKEND = "accounts.email_backend.ResendEmailBackend"
$env:RESEND_API_KEY = Read-Host "Resend API key"
$env:RESEND_FROM_EMAIL = "onboarding@resend.dev"
```

Remove them when finished:

```powershell
Remove-Item Env:DJANGO_EMAIL_BACKEND -ErrorAction SilentlyContinue
Remove-Item Env:RESEND_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:RESEND_FROM_EMAIL -ErrorAction SilentlyContinue
```

## What We Learned

```text
SMTP       -> needs an outbound mail connection
HTTPS API  -> sends through a normal web request
email      -> Django can use a custom backend
secret     -> API keys belong in environment variables
```

## Official References

- Resend send-email API: https://resend.com/docs/api-reference/emails/send-email
- Resend API keys: https://resend.com/docs/dashboard/api-keys
- Django custom email backends: https://docs.djangoproject.com/en/6.1/topics/email/

## Next Lesson

Next: deployment observability and a small health-check endpoint.
